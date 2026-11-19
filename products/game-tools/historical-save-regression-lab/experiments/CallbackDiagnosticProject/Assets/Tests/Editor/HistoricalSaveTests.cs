using NUnit.Framework;
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEngine;

public class HistoricalSaveTests
{
    private static string Fixture(string name) => Path.Combine(Application.dataPath, "Tests", "Fixtures", name);
    private static string Hash(string path) { using (var sha = SHA256.Create()) using (var stream = File.OpenRead(path)) return BitConverter.ToString(sha.ComputeHash(stream)); }

    [TestCase("v1.json", 3, false)]
    [TestCase("v2.json", 3, true)]
    [TestCase("v3.json", 4, true)]
    public void HistoricalSaveRestoresExpectedState(string name, int potions, bool questComplete)
    {
        var state = SampleSaveLoader.Load(File.ReadAllText(Fixture(name)));
        Assert.That(state.shield, Is.True, "inventory.unique.shield_01");
        Assert.That(state.potions, Is.EqualTo(potions), "inventory.potions");
        Assert.That(state.questComplete, Is.EqualTo(questComplete), "quests.complete");
    }

    [Test]
    public void NativeAssertionReportsSilentInventoryLoss()
    {
        var state = SampleSaveLoader.Load(File.ReadAllText(Fixture("v1.json")), introduceRegression: true);
        var failure = Assert.Throws<AssertionException>(() =>
            Assert.That(state.shield, Is.True, "inventory.unique.shield_01"));
        Assert.That(failure.Message, Does.Contain("inventory.unique.shield_01"));
    }

    [Test] public void FutureVersionIsRejected() =>
        Assert.Throws<System.ArgumentException>(() => SampleSaveLoader.Load("{\"version\":4}"));

    [TestCase("v1.json")][TestCase("v2.json")][TestCase("v3.json")]
    public void FiveDisposableCopiesLeaveSourceUnchanged(string name)
    {
        var source = Fixture(name);
        var before = Hash(source);
        for (var i = 0; i < 5; i++)
        {
            var dir = Path.Combine(Path.GetTempPath(), "gdm001-test-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(dir);
            try
            {
                var copy = Path.Combine(dir, name);
                File.Copy(source, copy);
                Assert.That(Hash(copy), Is.EqualTo(before));
                var state = SampleSaveLoader.Load(File.ReadAllText(copy));
                Assert.That(state.shield, Is.True);
                File.AppendAllText(copy, " ");
                Assert.That(Hash(source), Is.EqualTo(before));
            }
            finally { Directory.Delete(dir, true); }
        }
        Assert.That(Hash(source), Is.EqualTo(before));
    }
}
