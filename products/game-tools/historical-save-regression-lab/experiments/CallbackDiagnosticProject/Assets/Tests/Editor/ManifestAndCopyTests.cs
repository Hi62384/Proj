using System;
using System.IO;
using NUnit.Framework;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

public class ManifestAndCopyTests
{
    private const string Hash = "462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc";
    private static string Manifest => "{\"schema_version\":1,\"suite_id\":\"suite\",\"fixtures\":[{\"fixture_id\":\"v1\",\"file\":\"v1.json\",\"sha256\":\"" + Hash + "\",\"assertions\":[{\"path\":\"shield\",\"type\":\"boolean\",\"equals\":true}]}]}";
    private static string Root => Path.Combine(Application.dataPath, "Tests", "Fixtures");

    [Test] public void ParsesValidManifest() { var s = StrictManifest.Parse(Manifest); Assert.That(s.Id, Is.EqualTo("suite")); Assert.That(s.Fixtures[0].Assertions[0].Expected, Is.True); }
    [TestCase("\"schema_version\":1", "\"schema_version\":2")]
    [TestCase("\"schema_version\":1", "\"schema_version\":1,\"schema_version\":1")]
    [TestCase("\"suite_id\":\"suite\"", "\"suite_id\":\"suite\",\"unexpected\":0")]
    [TestCase("\"file\":\"v1.json\"", "\"file\":\"../v1.json\"")]
    [TestCase("\"equals\":true", "\"equals\":\"true\"")]
    [TestCase("\"equals\":true", "\"equals\":NaN")]
    public void RejectsInvalidManifest(string from, string to) => Assert.Throws<ArgumentException>(() => StrictManifest.Parse(Manifest.Replace(from, to)));
    [Test] public void RejectsDuplicateFixtureIds()
    {
        var fixture = "{\"fixture_id\":\"v1\",\"file\":\"v1.json\",\"sha256\":\"" + Hash + "\",\"assertions\":[{\"path\":\"shield\",\"type\":\"boolean\",\"equals\":true}]}";
        var json = "{\"schema_version\":1,\"suite_id\":\"suite\",\"fixtures\":[" + fixture + "," + fixture + "]}";
        Assert.Throws<ArgumentException>(() => StrictManifest.Parse(json));
    }
    [Test] public void RejectsTrailingData() => Assert.Throws<ArgumentException>(() => StrictManifest.Parse(Manifest + "{}"));
    [Test] public void RejectsSourceAsScratch() => Assert.Throws<ArgumentException>(() => FixtureCopy.Create(Root, StrictManifest.Parse(Manifest).Fixtures[0], Root));
    [Test] public void CopiesVerifiedBytesAndDeletesOnlyCopy()
    {
        var source = Path.Combine(Root, "v1.json"); var before = File.ReadAllBytes(source); string dir;
        using (var copy = FixtureCopy.Create(Root, StrictManifest.Parse(Manifest).Fixtures[0], Path.GetTempPath()))
        {
            dir = copy.DirectoryPath;
            CollectionAssert.AreEqual(before, File.ReadAllBytes(copy.FilePath));
            File.WriteAllText(copy.FilePath, "changed");
        }
        Assert.That(Directory.Exists(dir), Is.False); CollectionAssert.AreEqual(before, File.ReadAllBytes(source));
    }
    [Test] public void HashMismatchCreatesNoCopy()
    {
        var f = StrictManifest.Parse(Manifest).Fixtures[0]; f.Hash = new string('0', 64);
        Assert.Throws<ArgumentException>(() => FixtureCopy.Create(Root, f, Path.GetTempPath()));
    }
    private sealed class SampleAdapter : IAsyncSaveAdapter
    {
        public bool Called; private SampleSaveLoader.State state;
        public Task ResetAsync(CancellationToken cancellation) { Called = true; return Task.CompletedTask; }
        public async Task RestoreAsync(string path, CancellationToken cancellation) { await Task.Yield(); state = SampleSaveLoader.Load(File.ReadAllText(path), true); }
        public Task<IReadOnlyDictionary<string, object>> CaptureAsync(CancellationToken cancellation) => Task.FromResult<IReadOnlyDictionary<string, object>>(new Dictionary<string, object> { ["shield"] = state.shield });
    }
    [Test] public async Task RunnerDetectsSilentLossAndPreservesSource()
    {
        var before = File.ReadAllBytes(Path.Combine(Root, "v1.json"));
        var result = await ManifestRunner.RunAsync(Root, Path.GetTempPath(), StrictManifest.Parse(Manifest).Fixtures[0], new SampleAdapter(), CancellationToken.None);
        Assert.That(result.Status, Is.EqualTo("regression")); Assert.That(result.Path, Is.EqualTo("shield"));
        CollectionAssert.AreEqual(before, File.ReadAllBytes(Path.Combine(Root, "v1.json")));
    }
    [Test] public void InvalidHashStopsBeforeAdapter()
    {
        var f = StrictManifest.Parse(Manifest).Fixtures[0]; f.Hash = new string('0', 64); var adapter = new SampleAdapter();
        Assert.ThrowsAsync<ArgumentException>(async () => await ManifestRunner.RunAsync(Root, Path.GetTempPath(), f, adapter, CancellationToken.None));
        Assert.That(adapter.Called, Is.False);
    }
    private sealed class DelayedAdapter : IAsyncSaveAdapter
    {
        public readonly TaskCompletionSource<bool> Started = new TaskCompletionSource<bool>();
        public readonly TaskCompletionSource<bool> Finish = new TaskCompletionSource<bool>();
        public string CopyPath;
        public Task ResetAsync(CancellationToken token) => Task.CompletedTask;
        public async Task RestoreAsync(string path, CancellationToken token)
        {
            CopyPath = path; Started.TrySetResult(true);
            await Finish.Task; // Deliberately ignores cancellation.
        }
        public Task<IReadOnlyDictionary<string, object>> CaptureAsync(CancellationToken token) =>
            Task.FromResult<IReadOnlyDictionary<string, object>>(new Dictionary<string, object> { ["shield"] = true });
    }
    [Test] public async Task DeadlineKeepsCopyUntilUncooperativeAdapterFinishes()
    {
        var adapter = new DelayedAdapter();
        var run = ManifestRunner.RunAsync(Root, Path.GetTempPath(), StrictManifest.Parse(Manifest).Fixtures[0], adapter, CancellationToken.None, TimeSpan.FromMilliseconds  (100));
        await adapter.Started.Task;
        await Task.Delay(300);
        Assert.That(run.IsCompleted, Is.False);
        Assert.That(File.Exists(adapter.CopyPath), Is.True);
        adapter.Finish.SetResult(true);
        Assert.ThrowsAsync<TimeoutException>(async () => await run);
        Assert.That(File.Exists(adapter.CopyPath), Is.False);
    }
    [Test] public void RejectsInvalidDeadlineBeforeAdapter()
    {
        var adapter = new SampleAdapter();
        Assert.ThrowsAsync<ArgumentOutOfRangeException>(async () => await ManifestRunner.RunAsync(Root, Path.GetTempPath(), StrictManifest.Parse(Manifest).Fixtures[0], adapter, CancellationToken.None, TimeSpan.Zero));
        Assert.That(adapter.Called, Is.False);
    }

}
