using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

// Experimental orchestration only. The caller owns isolation and must await completion
// before deleting the sandbox. Adapters must honor Unity's main-thread requirements.
public interface IAsyncSaveAdapter
{
    Task ResetAsync(CancellationToken cancellation);
    Task RestoreAsync(string isolatedPath, CancellationToken cancellation);
    Task<IReadOnlyDictionary<string, object>> CaptureAsync(CancellationToken cancellation);
}

public static class AsyncAdapterSpike
{
    public static async Task<bool> RunAsync(IAsyncSaveAdapter adapter, string isolatedPath,
        string property, bool expected, CancellationToken cancellation)
    {
        if (adapter == null) throw new ArgumentNullException(nameof(adapter));
        cancellation.ThrowIfCancellationRequested();
        await adapter.ResetAsync(cancellation);
        cancellation.ThrowIfCancellationRequested();
        await adapter.RestoreAsync(isolatedPath, cancellation);
        cancellation.ThrowIfCancellationRequested();
        var state = await adapter.CaptureAsync(cancellation);
        cancellation.ThrowIfCancellationRequested();
        if (state == null || !state.TryGetValue(property, out var actual))
            throw new InvalidOperationException("Missing observed property: " + property);
        return actual is bool observed && observed == expected;
    }
}
