using System;
using NUnit.Framework;
using UnityEngine;

public class PrototypeReportTests
{
    [Serializable] private sealed class Report { public int schema_version, expected_count, completed_count; public string state; public bool success; public Item[] results; }
    [Serializable] private sealed class Item { public string fixture_id, status, path; }
    [Test] public void StableOrderingAndEscapingRoundTrip()
    {
        var a = new ManifestRunner.Result { FixtureId = "z\\\"id", Status = "regression", Path = "quest.\"name\"" };
        var b = new ManifestRunner.Result { FixtureId = "a", Status = "pass" };
        var expected = new[] { a.FixtureId, b.FixtureId };
        var first = PrototypeReport.SerializeSuite(expected,new[] { a, b },false);
        Assert.That(PrototypeReport.SerializeSuite(expected,new[] { b, a },false), Is.EqualTo(first));
        var parsed = JsonUtility.FromJson<Report>(first);
        Assert.That(parsed.schema_version, Is.EqualTo(1)); Assert.That(parsed.state,Is.EqualTo("complete")); Assert.That(parsed.success,Is.False);
        Assert.That(parsed.results[0].fixture_id, Is.EqualTo("a")); Assert.That(parsed.results[1].fixture_id, Is.EqualTo(a.FixtureId)); Assert.That(parsed.results[1].path, Is.EqualTo(a.Path));
        Assert.That(first, Does.Not.Contain("expected_value")); Assert.That(first, Does.Not.Contain("observed_value"));
    }
    [Test] public void IncompleteOrAbortedCannotPass()
    {
        var pass=new ManifestRunner.Result { FixtureId="a",Status="pass" }; var expected=new[]{"a","b"};
        Assert.Throws<ArgumentException>(()=>PrototypeReport.SerializeSuite(expected,new[]{pass},false));
        var partial=JsonUtility.FromJson<Report>(PrototypeReport.SerializeSuite(expected,new[]{pass},true));
        Assert.That(partial.state,Is.EqualTo("aborted")); Assert.That(partial.success,Is.False); Assert.That(partial.expected_count,Is.EqualTo(2)); Assert.That(partial.completed_count,Is.EqualTo(1));
        var empty=JsonUtility.FromJson<Report>(PrototypeReport.SerializeSuite(expected,new ManifestRunner.Result[0],true)); Assert.That(empty.success,Is.False);
        var completed=JsonUtility.FromJson<Report>(PrototypeReport.SerializeSuite(new[]{"a"},new[]{pass},false)); Assert.That(completed.success,Is.True);
    }
    [Test] public void RejectsMissingDuplicateAndInconsistentResults()
    {
        var pass = new ManifestRunner.Result { FixtureId = "a", Status = "pass" }; var expected=new[]{"a"};
        Assert.Throws<ArgumentException>(() => PrototypeReport.SerializeSuite(new string[0],new[]{pass},false));
        Assert.Throws<ArgumentException>(() => PrototypeReport.SerializeSuite(expected,new[] { pass, pass },false));
        Assert.Throws<ArgumentException>(() => PrototypeReport.SerializeSuite(expected,new[] { new ManifestRunner.Result { FixtureId = "x", Status = "pass" } },true));
        Assert.Throws<ArgumentException>(() => PrototypeReport.SerializeSuite(expected,new[] { new ManifestRunner.Result { FixtureId = "a", Status = "unknown" } },false));
        Assert.Throws<ArgumentException>(() => PrototypeReport.SerializeSuite(expected,new[] { new ManifestRunner.Result { FixtureId = "a", Status = "regression" } },false));
        Assert.Throws<ArgumentException>(() => PrototypeReport.SerializeSuite(expected,new[] { new ManifestRunner.Result { FixtureId = "a", Status = "pass", Path = "p" } },false));
    }
}
