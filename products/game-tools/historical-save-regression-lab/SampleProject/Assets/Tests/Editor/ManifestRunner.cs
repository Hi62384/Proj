using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

// Prototype: adapters are trusted code, not confined by the fixture copy.
public static class ManifestRunner
{
    public sealed class Result { public string FixtureId, Status, Path; }
    public sealed class AdapterException : Exception { public AdapterException(Exception inner) : base("Adapter failed", inner) { } }
    public static async Task<Result> RunAsync(string sourceRoot, string scratchRoot,
        StrictManifest.Fixture fixture, IAsyncSaveAdapter adapter, CancellationToken cancellation)
    {
        return await RunAsync(sourceRoot, scratchRoot, fixture, adapter, cancellation, Timeout.InfiniteTimeSpan);
    }

    // A deadline requests cancellation; it cannot stop an uncooperative adapter.
    // Await the adapter before disposing the copy, even after the deadline.
    public static async Task<Result> RunAsync(string sourceRoot, string scratchRoot,
        StrictManifest.Fixture fixture, IAsyncSaveAdapter adapter, CancellationToken cancellation, TimeSpan timeout)
    {
        if (timeout != Timeout.InfiniteTimeSpan && (timeout <= TimeSpan.Zero || timeout.TotalMilliseconds > int.MaxValue))
            throw new ArgumentOutOfRangeException(nameof(timeout));
        using (var deadline = new CancellationTokenSource())
        using (var linked = CancellationTokenSource.CreateLinkedTokenSource(cancellation, deadline.Token))
        {
            if (timeout != Timeout.InfiniteTimeSpan) deadline.CancelAfter(timeout);
            try
            {
                var result = await RunCoreAsync(sourceRoot, scratchRoot, fixture, adapter, linked.Token);
                cancellation.ThrowIfCancellationRequested();
                if (deadline.IsCancellationRequested) throw new TimeoutException("Adapter deadline elapsed; adapter has completed.");
                return result;
            }
            catch (OperationCanceledException) when (!cancellation.IsCancellationRequested && deadline.IsCancellationRequested)
            {
                throw new TimeoutException("Adapter deadline elapsed; adapter has completed.");
            }
        }
    }

    private static async Task<Result> RunCoreAsync(string sourceRoot, string scratchRoot,
        StrictManifest.Fixture fixture, IAsyncSaveAdapter adapter, CancellationToken cancellation)
    {
        if (fixture == null || adapter == null) throw new ArgumentNullException();
        cancellation.ThrowIfCancellationRequested();
        fixture = SnapshotAndValidate(fixture);
        // Complete copy and hash verification before invoking the adapter.
        using (var copy = FixtureCopy.Create(sourceRoot, fixture, scratchRoot))
        {
            IReadOnlyDictionary<string, object> state;
            try
            {
                await adapter.ResetAsync(cancellation);
                cancellation.ThrowIfCancellationRequested();
                await adapter.RestoreAsync(copy.FilePath, cancellation);
                cancellation.ThrowIfCancellationRequested();
                state = await adapter.CaptureAsync(cancellation);
                cancellation.ThrowIfCancellationRequested();
                if (state == null) throw new InvalidOperationException("Adapter returned no state");
            }
            catch (OperationCanceledException) { throw; }
            catch (Exception error) { throw new AdapterException(error); }
            foreach (var assertion in fixture.Assertions)
            {
                if (!state.TryGetValue(assertion.Path, out var actual)) throw new AdapterException(new InvalidOperationException("Missing observed property"));
                if (!Matches(assertion, actual)) return new Result { FixtureId = fixture.Id, Status = "regression", Path = assertion.Path };
            }
            return new Result { FixtureId = fixture.Id, Status = "pass" };
        }
    }
    // Public prototype models are mutable. Validate and snapshot before invoking
    // adapter code so a post-parse edit cannot create an empty or altered pass.
    private static StrictManifest.Fixture SnapshotAndValidate(StrictManifest.Fixture source)
    {
        if (String.IsNullOrWhiteSpace(source.Id) || source.Assertions == null || source.Assertions.Count == 0)
            throw new ArgumentException("Invalid fixture assertions");
        var copy = new StrictManifest.Fixture { Id = source.Id, File = source.File, Hash = source.Hash, Assertions = new List<StrictManifest.Assertion>() };
        var paths = new HashSet<string>(StringComparer.Ordinal);
        foreach (var a in source.Assertions)
        {
            if (a == null || String.IsNullOrWhiteSpace(a.Path) || !paths.Add(a.Path)) throw new ArgumentException("Invalid assertion path");
            if (Double.IsNaN(a.Tolerance) || Double.IsInfinity(a.Tolerance) || a.Tolerance < 0) throw new ArgumentException("Invalid tolerance");
            if (a.Expected is double n)
            {
                if (Double.IsNaN(n) || Double.IsInfinity(n) || Math.Abs(n) > 9007199254740991d) throw new ArgumentException("Invalid expected number");
            }
            else if (!(a.Expected is bool) && !(a.Expected is string)) throw new ArgumentException("Invalid expected type");
            else if (a.Tolerance != 0) throw new ArgumentException("Tolerance requires a number");
            copy.Assertions.Add(new StrictManifest.Assertion { Path = a.Path, Expected = a.Expected, Tolerance = a.Tolerance });
        }
        return copy;
    }
    // Deliberately narrow numeric representation: JSON numbers are doubles and
    // common Unity int/float/double values are accepted without string coercion.
    private static bool Matches(StrictManifest.Assertion assertion, object actual)
    {
        if (assertion.Expected is bool b) return actual is bool v && v == b;
        if (assertion.Expected is string s) return actual is string text && String.Equals(s, text, StringComparison.Ordinal);
        if (assertion.Expected is double expected)
        {
            double value;
            if (actual is int i) value = i;
            else if (actual is float f) value = f;
            else if (actual is double d) value = d;
            else return false;
            return !Double.IsNaN(value) && !Double.IsInfinity(value) && Math.Abs(value) <= 9007199254740991d && !Double.IsNaN(expected) && !Double.IsInfinity(expected)
                && !Double.IsNaN(assertion.Tolerance) && !Double.IsInfinity(assertion.Tolerance) && assertion.Tolerance >= 0
                && Math.Abs(value - expected) <= assertion.Tolerance;
        }
        return false;
    }
}
