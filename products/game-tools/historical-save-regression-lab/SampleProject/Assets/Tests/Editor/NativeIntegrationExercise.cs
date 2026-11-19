using System;
using System.IO;
using System.Security.Cryptography;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;

// Independent native-only integration exercise using the existing synthetic game loader.
public class NativeIntegrationExercise
{
    static string Digest(string path) { using (var h=SHA256.Create()) using (var s=File.OpenRead(path)) return BitConverter.ToString(h.ComputeHash(s)); }
    [TestCase("v1.json", 3, false)]
    [TestCase("v2.json", 3, true)]
    [TestCase("v3.json", 4, true)]
    public async Task RestoresExpectedState(string file, int potions, bool quest)
    {
        var source=Path.Combine(Application.dataPath,"Tests","Fixtures",file); var before=Digest(source);
        var directory=Path.Combine(Path.GetTempPath(),"gdm-native-"+Guid.NewGuid().ToString("N")); Directory.CreateDirectory(directory);
        try
        {
            var copy=Path.Combine(directory,file); File.Copy(source,copy);
            await Task.Yield(); var state=SampleSaveLoader.Load(File.ReadAllText(copy));
            Assert.That(state.shield,Is.True,"inventory.unique.shield_01");
            Assert.That(state.potions,Is.EqualTo(potions),"inventory.potions");
            Assert.That(state.potions > 0,Is.True,"inventory.has_potions");
            Assert.That(state.questComplete,Is.EqualTo(quest),"quests.complete");
        }
        finally { Directory.Delete(directory,true); }
        Assert.That(Digest(source),Is.EqualTo(before));
    }
}
