using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;

public class PrototypeSuiteTests
{
    private const string Hash="462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc";
    private static string Root => Path.Combine(Application.dataPath,"Tests","Fixtures");
    private static StrictManifest.Fixture Fixture(string id) => new StrictManifest.Fixture { Id=id, File="v1.json", Hash=Hash, Assertions=new List<StrictManifest.Assertion> { new StrictManifest.Assertion { Path="shield", Expected=true } } };
    private sealed class Adapter : IAsyncSaveAdapter
    {
        private readonly string behavior;
        public Adapter(string behavior) { this.behavior=behavior; }
        public Task ResetAsync(CancellationToken c) { if(behavior=="error") throw new ArgumentException("sensitive adapter detail"); return Task.CompletedTask; }
        public async Task RestoreAsync(string p,CancellationToken c) { if(behavior=="timeout") await Task.Delay(10000,c); }
        public Task<IReadOnlyDictionary<string,object>> CaptureAsync(CancellationToken c) => Task.FromResult<IReadOnlyDictionary<string,object>>(new Dictionary<string,object> { ["shield"]=behavior!="regression" });
    }
    [Test] public async Task SortsAndReportsDistinctOutcomesWithoutSecrets()
    {
        var bad=Fixture("b-invalid");bad.Hash=new string('0',64);
        var fixtures=new[]{Fixture("d-pass"),Fixture("c-error"),bad,Fixture("a-regression"),Fixture("e-timeout")};
        var results=await PrototypeSuite.RunAsync(Root,Path.GetTempPath(),fixtures,f => new Adapter(f.Id=="a-regression"?"regression":f.Id=="c-error"?"error":f.Id=="e-timeout"?"timeout":"pass"),TimeSpan.FromMilliseconds(100),CancellationToken.None);
        Assert.That(results.Count,Is.EqualTo(5));
        Assert.That(results[0].Status,Is.EqualTo("regression")); Assert.That(results[0].Path,Is.EqualTo("shield"));
        Assert.That(results[1].Status,Is.EqualTo("invalid_fixture")); Assert.That(results[2].Status,Is.EqualTo("adapter_error"));
        Assert.That(results[3].Status,Is.EqualTo("pass")); Assert.That(results[4].Status,Is.EqualTo("timeout"));
        var report=PrototypeReport.SerializeSuite(new[]{"a-regression","b-invalid","c-error","d-pass","e-timeout"},results,false); Assert.That(report,Does.Not.Contain("sensitive adapter detail")); Assert.That(report,Does.Contain("\"success\":false"));
    }
    [Test] public void RejectsDuplicateIdsBeforeFactory()
    {
        bool called=false;
        Assert.ThrowsAsync<ArgumentException>(async () => await PrototypeSuite.RunAsync(Root,Path.GetTempPath(),new[]{Fixture("a"),Fixture("a")},f => {called=true;return new Adapter("pass");},TimeSpan.FromSeconds(1),CancellationToken.None));
        Assert.That(called,Is.False);
    }
    [Test] public void ExternalCancellationDoesNotReturnCompleteReport()
    {
        Assert.CatchAsync<OperationCanceledException>(async () => await PrototypeSuite.RunAsync(Root,Path.GetTempPath(),new[]{Fixture("a")},f=>new Adapter("pass"),TimeSpan.FromSeconds(1),new CancellationToken(true)));
    }
}
