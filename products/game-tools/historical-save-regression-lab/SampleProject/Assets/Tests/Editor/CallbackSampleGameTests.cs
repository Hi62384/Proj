using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;

public class CallbackSampleGameTests
{
    private const string Hash="b4affb031dea089abdb0db963e8e503d821a8b72d92f6255d9ffc76ff70e6560";
    private static string Root => Path.Combine(Application.dataPath,"Tests","Fixtures");
    private static StrictManifest.Fixture Fixture() => new StrictManifest.Fixture { Id="callback-v1",File="alternate-v1.save",Hash=Hash,Assertions=new List<StrictManifest.Assertion>{new StrictManifest.Assertion{Path="inventory.sword",Expected=true},new StrictManifest.Assertion{Path="quest.started",Expected=true}} };
    private static string Digest(string path) { using(var hash=SHA256.Create()) using(var input=File.OpenRead(path)) return BitConverter.ToString(hash.ComputeHash(input)).Replace("-","").ToLowerInvariant(); }
    [TestCase(false,"pass")][TestCase(true,"regression")]
    public async Task WaitsForCallbackAndTestsState(bool fault,string expected)
    {
        var source=Path.Combine(Root,"alternate-v1.save"); var before=Digest(source); var game=new CallbackSampleGame();
        var run=ManifestRunner.RunAsync(Root,Path.GetTempPath(),Fixture(),new CallbackSampleAdapter(game,fault),CancellationToken.None);
        Assert.That(game.HasPending,Is.True); Assert.That(run.IsCompleted,Is.False); Assert.That(game.Current,Is.Null);
        game.FinishRestore();var result=await run;
        Assert.That(result.Status,Is.EqualTo(expected)); if(fault) Assert.That(result.Path,Is.EqualTo("inventory.sword"));
        Assert.That(game.HasPending,Is.False); Assert.That(Digest(source),Is.EqualTo(before)); Assert.That(before,Is.EqualTo(Hash));
    }
    [Test] public void CancellationStopsPendingRestoreBeforeReturn()
    {
        var game=new CallbackSampleGame();using(var cts=new CancellationTokenSource())
        {
            var run=ManifestRunner.RunAsync(Root,Path.GetTempPath(),Fixture(),new CallbackSampleAdapter(game),cts.Token);
            Assert.That(game.HasPending,Is.True); cts.Cancel();
            Assert.CatchAsync<OperationCanceledException>(async ()=>await run);
            Assert.That(game.HasPending,Is.False);Assert.That(game.Current,Is.Null);
        }
    }
}
