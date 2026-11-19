using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;

public class ScalarAssertionTests
{
    private const string Hash = "462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc";
    private static string Root => Path.Combine(Application.dataPath, "Tests", "Fixtures");
    private static StrictManifest.Fixture Fixture(string assertion) => StrictManifest.Parse("{\"schema_version\":1,\"suite_id\":\"s\",\"fixtures\":[{\"fixture_id\":\"v1\",\"file\":\"v1.json\",\"sha256\":\"" + Hash + "\",\"assertions\":[" + assertion + "]}]}").Fixtures[0];
    private sealed class Adapter : IAsyncSaveAdapter
    {
        private readonly object value;
        public Adapter(object value) { this.value = value; }
        public Task ResetAsync(CancellationToken c) => Task.CompletedTask;
        public Task RestoreAsync(string p, CancellationToken c) => Task.CompletedTask;
        public Task<IReadOnlyDictionary<string, object>> CaptureAsync(CancellationToken c) => Task.FromResult<IReadOnlyDictionary<string, object>>(new Dictionary<string, object> { ["value"] = value });
    }
    private static async Task<string> Run(string assertion, object actual) => (await ManifestRunner.RunAsync(Root, Path.GetTempPath(), Fixture(assertion), new Adapter(actual), CancellationToken.None)).Status;
    [TestCase(3, "pass")][TestCase(4, "regression")]
    public async Task NumberAssertionChecksInteger(int actual, string status) => Assert.That(await Run("{\"path\":\"value\",\"type\":\"number\",\"equals\":3}", actual), Is.EqualTo(status));
    [Test] public async Task ToleranceAndStrictTypes()
    {
        const string assertion = "{\"path\":\"value\",\"type\":\"number\",\"equals\":3,\"tolerance\":0.25}";
        Assert.That(await Run(assertion, 3.25), Is.EqualTo("pass"));
        Assert.That(await Run(assertion, 3.26), Is.EqualTo("regression"));
        Assert.That(await Run(assertion, "3"), Is.EqualTo("regression"));
        Assert.That(await Run(assertion, true), Is.EqualTo("regression"));
        Assert.That(await Run(assertion, double.NaN), Is.EqualTo("regression"));
    }
    [Test] public async Task StringsCompareOrdinally()
    {
        const string assertion = "{\"path\":\"value\",\"type\":\"string\",\"equals\":\"Shield\"}";
        Assert.That(await Run(assertion, "Shield"), Is.EqualTo("pass"));
        Assert.That(await Run(assertion, "shield"), Is.EqualTo("regression"));
        Assert.That(await Run(assertion, 3), Is.EqualTo("regression"));
    }
    [TestCase("{\"path\":\"value\",\"type\":\"number\",\"equals\":3,\"tolerance\":-1}")]
    [TestCase("{\"path\":\"value\",\"type\":\"number\",\"equals\":3,\"tolerance\":1e999}")]
    [TestCase("{\"path\":\"value\",\"type\":\"boolean\",\"equals\":true,\"tolerance\":0}")]
    [TestCase("{\"path\":\"value\",\"type\":\"number\",\"equals\":\"3\"}")]
    [TestCase("{\"path\":\"value\",\"type\":\"string\",\"equals\":false}")]
    public void RejectsInvalidScalarAssertion(string assertion) => Assert.Throws<ArgumentException>(() => Fixture(assertion));

    private sealed class MutatingAdapter : IAsyncSaveAdapter
    {
        private readonly StrictManifest.Fixture fixture;
        public bool Called;
        public MutatingAdapter(StrictManifest.Fixture fixture) { this.fixture = fixture; }
        public Task ResetAsync(CancellationToken c) { Called = true; fixture.Assertions.Clear(); return Task.CompletedTask; }
        public Task RestoreAsync(string p, CancellationToken c) => Task.CompletedTask;
        public Task<IReadOnlyDictionary<string, object>> CaptureAsync(CancellationToken c) => Task.FromResult<IReadOnlyDictionary<string, object>>(new Dictionary<string, object> { ["value"] = false });
    }
    [Test] public async Task AdapterCannotEraseAssertionsDuringRun()
    {
        var fixture = Fixture("{\"path\":\"value\",\"type\":\"boolean\",\"equals\":true}");
        var result = await ManifestRunner.RunAsync(Root, Path.GetTempPath(), fixture, new MutatingAdapter(fixture), CancellationToken.None);
        Assert.That(result.Status, Is.EqualTo("regression"));
        Assert.That(result.Path, Is.EqualTo("value"));
    }
    [Test] public void EmptyMutatedAssertionsRejectedBeforeAdapter()
    {
        var fixture = Fixture("{\"path\":\"value\",\"type\":\"boolean\",\"equals\":true}");
        fixture.Assertions.Clear(); var adapter = new MutatingAdapter(fixture);
        Assert.ThrowsAsync<ArgumentException>(async () => await ManifestRunner.RunAsync(Root, Path.GetTempPath(), fixture, adapter, CancellationToken.None));
        Assert.That(adapter.Called, Is.False);
    }
    [Test] public void InvalidMutatedToleranceRejectedBeforeAdapter()
    {
        var fixture = Fixture("{\"path\":\"value\",\"type\":\"number\",\"equals\":3}");
        fixture.Assertions[0].Tolerance = double.NaN; var adapter = new MutatingAdapter(fixture);
        Assert.ThrowsAsync<ArgumentException>(async () => await ManifestRunner.RunAsync(Root, Path.GetTempPath(), fixture, adapter, CancellationToken.None));
        Assert.That(adapter.Called, Is.False);
    }

    [TestCase("9007199254740992")]
    [TestCase("9007199254740993")]
    [TestCase("9.007199254740993e15")]
    [TestCase("-9007199254740993")]
    public void RejectsUnsafeMagnitudeBeforeComparison(string number)
    {
        var json = "{\"path\":\"value\",\"type\":\"number\",\"equals\":" + number + "}";
        Assert.Throws<ArgumentException>(() => Fixture(json));
    }
    [Test] public async Task UnsafeObservedMagnitudeCannotPass()
    {
        var json = "{\"path\":\"value\",\"type\":\"number\",\"equals\":9007199254740991,\"tolerance\":2}";
        Assert.That(await Run(json, 9007199254740992d), Is.EqualTo("regression"));
        Assert.That(await Run(json, 9007199254740991d), Is.EqualTo("pass"));
    }
}
