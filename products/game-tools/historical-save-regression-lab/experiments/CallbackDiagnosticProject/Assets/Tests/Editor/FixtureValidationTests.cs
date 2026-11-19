using System;
using System.IO;
using NUnit.Framework;
using UnityEngine;

public class FixtureValidationTests
{
    private static string Root => Path.Combine(Application.dataPath, "Tests", "Fixtures");
    private static FixtureValidation.Fixture Good() => new FixtureValidation.Fixture { Id = "v1", FileName = "v1.json", Sha256 = "462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc" };
    [Test] public void ValidFixturePasses() => FixtureValidation.Validate(Root, 1, new[] { Good() });
    [Test] public void DuplicateIdsFail() => Assert.Throws<ArgumentException>(() => FixtureValidation.Validate(Root, 1, new[] { Good(), Good() }));
    [Test] public void FutureSchemaFails() => Assert.Throws<ArgumentException>(() => FixtureValidation.Validate(Root, 2, new[] { Good() }));
    [Test] public void WrongHashFails() { var f = Good(); f.Sha256 = new string('0', 64); Assert.Throws<ArgumentException>(() => FixtureValidation.Validate(Root, 1, new[] { f })); }
    [TestCase("../v1.json")][TestCase("C:\\v1.json")][TestCase("sub/v1.json")][TestCase("..")] public void UnsafePathFails(string path) { var f = Good(); f.FileName = path; Assert.Throws<ArgumentException>(() => FixtureValidation.Validate(Root, 1, new[] { f })); }
}
