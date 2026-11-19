using System;
using System.IO;
using NUnit.Framework;
using UnityEngine;

public class PrototypeRunnerTests
{
    private static string Root => Path.Combine(Application.dataPath, "Tests", "Fixtures");
    private static FixtureValidation.Fixture Fixture() => new FixtureValidation.Fixture { Id = "v1", FileName = "v1.json", Sha256 = "462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc" };
    [Test] public void GoodSavePasses() => Assert.That(PrototypeRunner.Run(Root, Fixture(), false).Status, Is.EqualTo("pass"));
    [Test] public void SilentLossHasPath() { var r = PrototypeRunner.Run(Root, Fixture(), true); Assert.That(r.Status, Is.EqualTo("regression")); Assert.That(r.Path, Is.EqualTo("inventory.unique.shield_01")); }
    [Test] public void InvalidHashStopsBeforeLoad() { var f = Fixture(); f.Sha256 = new string('0', 64); Assert.Throws<ArgumentException>(() => PrototypeRunner.Run(Root, f, false)); }
}
