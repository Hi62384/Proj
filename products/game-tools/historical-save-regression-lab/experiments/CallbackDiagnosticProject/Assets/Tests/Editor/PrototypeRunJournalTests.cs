using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;

public class PrototypeRunJournalTests
{
    private string root;
    [SetUp] public void Setup() { root=Path.Combine(Path.GetTempPath(),"gdm-journal-test-"+Guid.NewGuid().ToString("N")); Directory.CreateDirectory(root); }
    [TearDown] public void Teardown() { if(Directory.Exists(root)) Directory.Delete(root,true); }
    [Test] public void AbandonedRunIsVisibleAsIncomplete()
    {
        var journal=PrototypeRunJournal.Begin(root);
        Assert.That(File.Exists(journal.IncompletePath),Is.True); Assert.That(File.Exists(journal.CompletePath),Is.False);
        var marker=File.ReadAllText(journal.IncompletePath); Assert.That(marker,Does.Contain("\"state\":\"incomplete\"")); Assert.That(marker,Does.Contain("\"success\":false"));
    }
    [Test] public void OnlyACompleteValidatedResultCanBePublished()
    {
        var journal=PrototypeRunJournal.Begin(root); var pass=new ManifestRunner.Result { FixtureId="a",Status="pass" };
        Assert.Throws<ArgumentException>(()=>journal.Complete(new[]{"a","b"},new[]{pass})); Assert.That(File.Exists(journal.CompletePath),Is.False);
        journal.Complete(new[]{"a"},new[]{pass}); Assert.That(File.ReadAllText(journal.CompletePath),Does.Contain("\"state\":\"complete\""));
        Assert.Throws<IOException>(()=>journal.Complete(new[]{"a"},new[]{pass}));
    }
    [Test] public void CancellationLeavesIncompleteMarkerAndNoCompleteReport()
    {
        var journal=PrototypeRunJournal.Begin(root);
        var f=new StrictManifest.Fixture { Id="a",File="v1.json",Hash=new string('0',64),Assertions=new List<StrictManifest.Assertion>{new StrictManifest.Assertion{Path="p",Expected=true}} };
        Assert.CatchAsync<OperationCanceledException>(async ()=>await PrototypeSuite.RunRecordedAsync(Application.dataPath,root,new[]{f},x=>null,TimeSpan.FromSeconds(1),new CancellationToken(true),journal));
        Assert.That(File.Exists(journal.IncompletePath),Is.True); Assert.That(File.Exists(journal.CompletePath),Is.False);
    }

    [Test] public void InspectorFailsClosedOnPartialOrContradictoryFiles()
    {
        var journal=PrototypeRunJournal.Begin(root); var ids=new[]{"a","b"};
        Assert.That(PrototypeRunJournal.Inspect(journal.DirectoryPath,ids),Is.EqualTo("incomplete"));
        File.WriteAllText(Path.Combine(journal.DirectoryPath,"orphan.tmp"),"{broken");
        Assert.That(PrototypeRunJournal.Inspect(journal.DirectoryPath,ids),Is.EqualTo("incomplete"));
        File.WriteAllText(journal.CompletePath,"{broken");
        Assert.That(PrototypeRunJournal.Inspect(journal.DirectoryPath,ids),Is.EqualTo("invalid"));
        File.WriteAllText(journal.CompletePath,"{\"schema_version\":1,\"schema_version\":1}");
        Assert.That(PrototypeRunJournal.Inspect(journal.DirectoryPath,ids),Is.EqualTo("invalid"));
    }
    [Test] public void InspectorChecksFixtureSetAndComputedOutcome()
    {
        var journal=PrototypeRunJournal.Begin(root);var pass=new ManifestRunner.Result{FixtureId="a",Status="pass"};
        journal.Complete(new[]{"a"},new[]{pass});
        Assert.That(PrototypeRunJournal.Inspect(journal.DirectoryPath,new[]{"a"}),Is.EqualTo("complete_pass"));
        Assert.That(PrototypeRunJournal.Inspect(journal.DirectoryPath,new[]{"a","b"}),Is.EqualTo("invalid"));
        var json=File.ReadAllText(journal.CompletePath).Replace("\"success\":true","\"success\":false"); File.WriteAllText(journal.CompletePath,json);
        Assert.That(PrototypeRunJournal.Inspect(journal.DirectoryPath,new[]{"a"}),Is.EqualTo("invalid"));
        var failure=PrototypeRunJournal.Begin(root);failure.Complete(new[]{"a"},new[]{new ManifestRunner.Result{FixtureId="a",Status="regression",Path="shield"}});
        Assert.That(PrototypeRunJournal.Inspect(failure.DirectoryPath,new[]{"a"}),Is.EqualTo("complete_fail"));
    }

    [Test] public void CiMappingFailsClosedForIncompleteInvalidAndRegression()
    {
        var j=PrototypeRunJournal.Begin(root);var ids=new[]{"a"};
        Assert.That(PrototypeJournalCi.ExitCode(j.DirectoryPath,ids),Is.EqualTo(1));
        j.Complete(ids,new[]{new ManifestRunner.Result{FixtureId="a",Status="pass"}});
        Assert.That(PrototypeJournalCi.ExitCode(j.DirectoryPath,ids),Is.EqualTo(0));
        File.WriteAllText(j.CompletePath,"broken"); Assert.That(PrototypeJournalCi.ExitCode(j.DirectoryPath,ids),Is.EqualTo(1));
        var failed=PrototypeRunJournal.Begin(root);failed.Complete(ids,new[]{new ManifestRunner.Result{FixtureId="a",Status="regression",Path="shield"}});
        Assert.That(PrototypeJournalCi.ExitCode(failed.DirectoryPath,ids),Is.EqualTo(1));
    }
}
