using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;

// Independent prototype-only exercise; adapter calls the same synthetic loader.
public class PrototypeIntegrationExercise
{
    private sealed class Adapter : IAsyncSaveAdapter
    {
        private SampleSaveLoader.State state;
        public Task ResetAsync(CancellationToken c) { state=null; return Task.CompletedTask; }
        public async Task RestoreAsync(string path, CancellationToken c) { await Task.Yield(); state=SampleSaveLoader.Load(File.ReadAllText(path)); }
        public Task<IReadOnlyDictionary<string,object>> CaptureAsync(CancellationToken c) => Task.FromResult<IReadOnlyDictionary<string,object>>(new Dictionary<string,object> {
            ["inventory.unique.shield_01"]=state.shield, ["inventory.potions"]=state.potions, ["inventory.has_potions"]=state.potions > 0, ["quests.complete"]=state.questComplete
        });
    }
    [TestCase("v1.json","462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc",3,false)]
    [TestCase("v2.json","aad6fb81678b3cd0bc49669338d61acfc9bd43a4101e31c767acf030f9ee04a5",3,true)]
    [TestCase("v3.json","c93bf46eedaf15bd39329f66bb25199c846237d18affc657e2d50fddbc23cab1",4,true)]
    public async Task RestoresExpectedState(string file,string hash,int potions,bool quest)
    {
        var manifest="{\"schema_version\":1,\"suite_id\":\"integration\",\"fixtures\":[{\"fixture_id\":\"fixture\",\"file\":\""+file+"\",\"sha256\":\""+hash+"\",\"assertions\":[{\"path\":\"inventory.unique.shield_01\",\"type\":\"boolean\",\"equals\":true},{\"path\":\"inventory.potions\",\"type\":\"number\",\"equals\":"+potions+"},{\"path\":\"inventory.has_potions\",\"type\":\"boolean\",\"equals\":true},{\"path\":\"quests.complete\",\"type\":\"boolean\",\"equals\":"+(quest?"true":"false")+"}]}]}";
        var fixture=StrictManifest.Parse(manifest).Fixtures[0];
        var result=await ManifestRunner.RunAsync(Path.Combine(Application.dataPath,"Tests","Fixtures"),Path.GetTempPath(),fixture,new Adapter(),CancellationToken.None);
        Assert.That(result.Status,Is.EqualTo("pass"),result.Path);
    }
}
