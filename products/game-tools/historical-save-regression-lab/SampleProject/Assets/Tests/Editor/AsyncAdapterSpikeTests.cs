using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NUnit.Framework;

public class AsyncAdapterSpikeTests
{
    private sealed class Adapter : IAsyncSaveAdapter
    {
        public readonly TaskCompletionSource<bool> Completion = new TaskCompletionSource<bool>();
        public bool Captured;
        public Task ResetAsync(CancellationToken cancellation) => Task.CompletedTask;
        public async Task RestoreAsync(string path, CancellationToken cancellation) { await Completion.Task; }
        public Task<IReadOnlyDictionary<string, bool>> CaptureAsync(CancellationToken cancellation)
        {
            Captured = true;
            return Task.FromResult<IReadOnlyDictionary<string, bool>>(new Dictionary<string, bool> { ["shield"] = false });
        }
    }

    private sealed class FailingAdapter : IAsyncSaveAdapter
    {
        public bool Captured;
        public Task ResetAsync(CancellationToken cancellation) => Task.CompletedTask;
        public Task RestoreAsync(string path, CancellationToken cancellation) => Task.FromException(new InvalidOperationException("restore failed"));
        public Task<IReadOnlyDictionary<string, bool>> CaptureAsync(CancellationToken cancellation)
        {
            Captured = true;
            return Task.FromResult<IReadOnlyDictionary<string, bool>>(new Dictionary<string, bool>());
        }
    }

    [Test] public async Task WaitsForCompletionAndFindsRegression()
    {
        var adapter = new Adapter();
        var run = AsyncAdapterSpike.RunAsync(adapter, "copy", "shield", true, CancellationToken.None);
        Assert.That(run.IsCompleted, Is.False);
        Assert.That(adapter.Captured, Is.False);
        adapter.Completion.SetResult(true);
        Assert.That(await run, Is.False);
        Assert.That(adapter.Captured, Is.True);
    }

    [Test] public void CancellationBeforeResetStopsRun()
    {
        var adapter = new Adapter();
        var cancellation = new CancellationToken(true);
        Assert.CatchAsync<OperationCanceledException>(async () => await AsyncAdapterSpike.RunAsync(adapter, "copy", "shield", true, cancellation));
        Assert.That(adapter.Captured, Is.False);
    }

    [Test] public void RestoreErrorDoesNotCaptureState()
    {
        var adapter = new FailingAdapter();
        Assert.ThrowsAsync<InvalidOperationException>(async () => await AsyncAdapterSpike.RunAsync(adapter, "copy", "shield", true, CancellationToken.None));
        Assert.That(adapter.Captured, Is.False);
    }

    [Test] public async Task MissingPropertyIsAnError()
    {
        var adapter = new Adapter();
        adapter.Completion.SetResult(true);
        var run = AsyncAdapterSpike.RunAsync(adapter, "copy", "missing", true, CancellationToken.None);
        try { await run; Assert.Fail("Missing property must not pass"); }
        catch (InvalidOperationException error) { StringAssert.Contains("missing", error.Message); }
    }
}
