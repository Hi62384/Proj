using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

// Experimental sequential orchestration for trusted synthetic adapters only.
// Timeout remains cooperative: an adapter that ignores cancellation can hang.
public static class PrototypeSuite
{
    public static async Task<IReadOnlyList<ManifestRunner.Result>> RunAsync(string root, string scratch,
        IEnumerable<StrictManifest.Fixture> fixtures, Func<StrictManifest.Fixture,IAsyncSaveAdapter> factory,
        TimeSpan timeout, CancellationToken cancellation)
    {
        if (fixtures == null || factory == null) throw new ArgumentNullException();
        if (timeout != Timeout.InfiniteTimeSpan && (timeout <= TimeSpan.Zero || timeout.TotalMilliseconds > int.MaxValue)) throw new ArgumentOutOfRangeException(nameof(timeout));
        var all = fixtures.ToArray();
        if (all.Length == 0 || all.Any(x => x == null || String.IsNullOrWhiteSpace(x.Id)) || all.Select(x => x.Id).Distinct(StringComparer.Ordinal).Count() != all.Length)
            throw new ArgumentException("Invalid suite fixture ids");
        var results = new List<ManifestRunner.Result>();
        foreach (var fixture in all.OrderBy(x => x.Id, StringComparer.Ordinal))
        {
            cancellation.ThrowIfCancellationRequested();
            try
            {
                IAsyncSaveAdapter adapter;
                try { adapter = factory(fixture); if (adapter == null) throw new InvalidOperationException(); }
                catch (OperationCanceledException) { throw; }
                catch (Exception error) { throw new ManifestRunner.AdapterException(error); }
                results.Add(await ManifestRunner.RunAsync(root,scratch,fixture,adapter,cancellation,timeout));
            }
            catch (OperationCanceledException) { throw; }
            catch (TimeoutException) { results.Add(Failure(fixture.Id,"timeout")); }
            catch (ManifestRunner.AdapterException) { results.Add(Failure(fixture.Id,"adapter_error")); }
            catch (ArgumentException) { results.Add(Failure(fixture.Id,"invalid_fixture")); }
            catch (Exception) { results.Add(Failure(fixture.Id,"runner_error")); }
        }
        return results;
    }
    // The caller creates the journal first so its path remains available if
    // cancellation or an exception prevents a final report.
    public static async Task<IReadOnlyList<ManifestRunner.Result>> RunRecordedAsync(string root, string scratch,
        IEnumerable<StrictManifest.Fixture> fixtures, Func<StrictManifest.Fixture,IAsyncSaveAdapter> factory,
        TimeSpan timeout, CancellationToken cancellation, PrototypeRunJournal journal)
    {
        if (journal == null || fixtures == null) throw new ArgumentNullException();
        var all = fixtures.ToArray();
        var ids = all.Select(x => x == null ? null : x.Id).ToArray();
        var results = await RunAsync(root,scratch,all,factory,timeout,cancellation);
        cancellation.ThrowIfCancellationRequested();
        journal.Complete(ids,results);
        return results;
    }
    private static ManifestRunner.Result Failure(string id,string status) => new ManifestRunner.Result { FixtureId=id, Status=status };
}
