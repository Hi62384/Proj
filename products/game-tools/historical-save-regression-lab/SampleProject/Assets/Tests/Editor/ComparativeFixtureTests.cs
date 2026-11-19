using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;

// A controlled, partial head-to-head: both paths use the same synthetic loader,
// asynchronous completion and two injected faults. Not a real game or sandbox.
public class ComparativeFixtureTests
{
    private static string Root => Path.Combine(Application.dataPath, "Tests", "Fixtures");
    private static string Hash(string path) { using (var h = SHA256.Create()) using (var s = File.OpenRead(path)) return BitConverter.ToString(h.ComputeHash(s)).Replace("-", "").ToLowerInvariant(); }
    private static async Task<SampleSaveLoader.State> LoadAsync(string path, string fault)
    {
        await Task.Yield();
        var state = SampleSaveLoader.Load(File.ReadAllText(path), fault == "shield");
        if (fault == "quest") state.questComplete = false;
        if (fault == "potions") state.potions = 0;
        return state;
    }
    private sealed class Adapter : IAsyncSaveAdapter
    {
        private readonly string fault;
        private SampleSaveLoader.State state;
        public Adapter(string fault) { this.fault = fault; }
        public Task ResetAsync(CancellationToken token) { state = null; return Task.CompletedTask; }
        public async Task RestoreAsync(string path, CancellationToken token) { state = await LoadAsync(path, fault); }
        public Task<IReadOnlyDictionary<string, object>> CaptureAsync(CancellationToken token) => Task.FromResult<IReadOnlyDictionary<string, object>>(new Dictionary<string, object> { ["inventory.unique.shield_01"] = state.shield, ["quests.complete"] = state.questComplete, ["inventory.potions"] = state.potions });
    }
    [TestCase("v1.json", false, 3, "none", null)]
    [TestCase("v2.json", true, 3, "none", null)]
    [TestCase("v3.json", true, 4, "none", null)]
    [TestCase("v1.json", false, 3, "shield", "inventory.unique.shield_01")]
    [TestCase("v2.json", true, 3, "quest", "quests.complete")]
    [TestCase("v3.json", true, 4, "potions", "inventory.potions")]
    public async Task NativeAndPrototypeDetectSameCases(string name, bool expectedQuest, int expectedPotions, string fault, string failedPath)
    {
        var source = Path.Combine(Root, name); var before = Hash(source);
        // Native baseline uses a distinct disposable copy and direct assertions.
        var temp = Path.Combine(Path.GetTempPath(), "gdm001-comparison-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(temp);
        try
        {
            var copy = Path.Combine(temp, name); File.Copy(source, copy);
            var native = await LoadAsync(copy, fault);
            TestDelegate checks = () => { Assert.That(native.shield, Is.True, "inventory.unique.shield_01"); Assert.That(native.questComplete, Is.EqualTo(expectedQuest), "quests.complete"); Assert.That(native.potions, Is.EqualTo(expectedPotions), "inventory.potions"); };
            if (failedPath == null) checks();
            else { var failure = Assert.Throws<AssertionException>(checks); Assert.That(failure.Message, Does.Contain(failedPath)); }
        }
        finally { Directory.Delete(temp, true); }
        var fixture = new StrictManifest.Fixture { Id = name, File = name, Hash = before, Assertions = new List<StrictManifest.Assertion> {
            new StrictManifest.Assertion { Path = "inventory.unique.shield_01", Expected = true },
            new StrictManifest.Assertion { Path = "quests.complete", Expected = expectedQuest },
            new StrictManifest.Assertion { Path = "inventory.potions", Expected = (double)expectedPotions }
        }};
        var result = await ManifestRunner.RunAsync(Root, Path.GetTempPath(), fixture, new Adapter(fault), CancellationToken.None);
        Assert.That(result.Status, Is.EqualTo(failedPath == null ? "pass" : "regression"));
        Assert.That(result.Path, Is.EqualTo(failedPath));
        Assert.That(Hash(source), Is.EqualTo(before));
    }

    // Opt in only for isolated CLI experiments. A genuine failure must propagate
    // through Unity's test runner rather than being caught by the positive suite.
    private static void RequireNegativeRun()
    {
        if (Environment.GetEnvironmentVariable("GDM001_NEGATIVE_CI") != "1")
            Assert.Ignore("Intentional negative CI experiment is opt-in");
    }
    [Test] public async Task NativeCliFailure()
    {
        RequireNegativeRun();
        var directory = Path.Combine(Path.GetTempPath(), "gdm001-ci-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(directory);
        try
        {
            var copy = Path.Combine(directory, "v1.json");
            File.Copy(Path.Combine(Root, "v1.json"), copy);
            var state = await LoadAsync(copy, "shield");
            Assert.That(state.shield, Is.True, "inventory.unique.shield_01");
        }
        finally { Directory.Delete(directory, true); }
    }
    [Test] public async Task PrototypeCliFailure()
    {
        RequireNegativeRun();
        var source = Path.Combine(Root, "v1.json");
        var fixture = new StrictManifest.Fixture { Id = "v1", File = "v1.json", Hash = Hash(source), Assertions = new List<StrictManifest.Assertion> {
            new StrictManifest.Assertion { Path = "inventory.unique.shield_01", Expected = true }
        }};
        var result = await ManifestRunner.RunAsync(Root, Path.GetTempPath(), fixture, new Adapter("shield"), CancellationToken.None);
        Assert.That(result.Status, Is.EqualTo("pass"), result.Path);
    }
}
