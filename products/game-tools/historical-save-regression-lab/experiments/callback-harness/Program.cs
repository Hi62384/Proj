using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.IO;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;

public interface IAsyncSaveAdapter
{
    Task ResetAsync(CancellationToken c);
    Task RestoreAsync(string path,CancellationToken c);
    Task<IReadOnlyDictionary<string,object>> CaptureAsync(CancellationToken c);
}
public static class Program
{
    static void Check(bool value,string message) { if(!value) throw new InvalidOperationException(message); }
    private sealed class PumpContext : SynchronizationContext
    {
        private readonly ConcurrentQueue<Action> queue=new ConcurrentQueue<Action>();
        public override void Post(SendOrPostCallback callback,object state) => queue.Enqueue(()=>callback(state));
        public int Drain() { int count=0;while(queue.TryDequeue(out var action)) { action(); count++; } return count; }
    }
    static void CheckPostedCancellation(string path)
    {
        var previous=SynchronizationContext.Current; var context=new PumpContext(); SynchronizationContext.SetSynchronizationContext(context);
        try
        {
            var game=new CallbackSampleGame(); var adapter=new CallbackSampleAdapter(game); using(var cts=new CancellationTokenSource())
            {
                var run=adapter.RestoreAsync(path,cts.Token); Check(game.HasPending && !run.IsCompleted,"callback not pending");
                Task.Run(()=>cts.Cancel()).GetAwaiter().GetResult();
                Check(!run.IsCompleted,"continuation unexpectedly bypassed captured context");
                Check(context.Drain()>0,"cancellation continuation was not posted");
                Check(run.IsCanceled && !game.HasPending,"pumped cancellation did not clear pending callback");
            }
        }
        finally { SynchronizationContext.SetSynchronizationContext(previous); }
        Console.WriteLine("posted cancellation required context pump and then completed");
    }
    public static async Task Main(string[] args)
    {
        if(args.Length!=1) throw new ArgumentException("synthetic fixture path required");
        var path=args[0];var before=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
        foreach(var fault in new[]{false,true})
        {
            var game=new CallbackSampleGame();var adapter=new CallbackSampleAdapter(game,fault);
            await adapter.ResetAsync(CancellationToken.None);
            var restore=adapter.RestoreAsync(path,CancellationToken.None);
            Check(game.HasPending && !restore.IsCompleted && game.Current==null,"must await callback");
            game.FinishRestore();await restore;
            var state=await adapter.CaptureAsync(CancellationToken.None);
            Check((bool)state["inventory.sword"]==!fault && (bool)state["quest.started"],"unexpected state");
            Check(!game.HasPending,"pending callback leaked");
            Console.WriteLine(fault?"fault detected":"normal restore passed");
        }
        var pending=new CallbackSampleGame();var cancelAdapter=new CallbackSampleAdapter(pending);using(var cts=new CancellationTokenSource())
        {
            await cancelAdapter.ResetAsync(cts.Token);var run=cancelAdapter.RestoreAsync(path,cts.Token);
            Check(pending.HasPending,"expected pending callback");cts.Cancel();
            try { await run; throw new InvalidOperationException("cancellation did not propagate"); } catch(OperationCanceledException) { }
            Check(!pending.HasPending && pending.Current==null,"cancel did not abort callback");
        }
        Check(Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)))==before,"fixture changed");
        Console.WriteLine("cancellation and fixture hash checks passed");
        CheckPostedCancellation(path);
    }
}
