using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

// Original synthetic callback-style game. Only this sample format is supported.
public sealed class CallbackSampleGame
{
    public sealed class State { public bool Sword; public bool QuestStarted; }
    public State Current { get; private set; }
    private Action pending;
    public bool HasPending => pending != null;
    public void Reset() { pending=null; Current=null; }
    public void BeginRestore(string path, bool fault, Action completed)
    {
        if (pending != null) throw new InvalidOperationException("Restore already pending");
        var values=new Dictionary<string,string>(StringComparer.Ordinal);
        foreach (var line in File.ReadAllLines(path))
        {
            if (String.IsNullOrWhiteSpace(line)) continue;
            var parts=line.Split('='); if (parts.Length!=2 || values.ContainsKey(parts[0])) throw new FormatException("Invalid synthetic save");
            values.Add(parts[0],parts[1]);
        }
        if (!values.TryGetValue("schema",out var version) || version!="1" || !values.TryGetValue("inventory.sword",out var sword) || !values.TryGetValue("quest.started",out var quest) || (sword!="0" && sword!="1") || (quest!="0" && quest!="1")) throw new FormatException("Invalid synthetic save");
        // Completion is signaled by the game, not by a timer or assumed frame count.
        pending=()=>{ Current=new State { Sword=!fault && sword=="1", QuestStarted=quest=="1" }; completed(); };
    }
    public void FinishRestore() { var action=pending ?? throw new InvalidOperationException("No pending restore"); pending=null; action(); }
    public void AbortRestore() { pending=null; }
}

// Adapter is experimental and assumes all game operations execute on Unity's main thread.
public sealed class CallbackSampleAdapter : IAsyncSaveAdapter
{
    private readonly CallbackSampleGame game; private readonly bool fault;
    public CallbackSampleAdapter(CallbackSampleGame game,bool fault=false) { this.game=game;this.fault=fault; }
    public Task ResetAsync(CancellationToken cancellation) { cancellation.ThrowIfCancellationRequested(); game.Reset(); return Task.CompletedTask; }
    public async Task RestoreAsync(string path,CancellationToken cancellation)
    {
        cancellation.ThrowIfCancellationRequested();
        var completion=new TaskCompletionSource<bool>();
        game.BeginRestore(path,fault,()=>completion.TrySetResult(true));
        try { using (cancellation.Register(()=>completion.TrySetCanceled())) await completion.Task; }
        finally { game.AbortRestore(); }
    }
    public Task<IReadOnlyDictionary<string,object>> CaptureAsync(CancellationToken cancellation)
    {
        cancellation.ThrowIfCancellationRequested();
        if (game.Current==null) throw new InvalidOperationException("No restored state");
        return Task.FromResult<IReadOnlyDictionary<string,object>>(new Dictionary<string,object> { ["inventory.sword"]=game.Current.Sword,["quest.started"]=game.Current.QuestStarted });
    }
}
