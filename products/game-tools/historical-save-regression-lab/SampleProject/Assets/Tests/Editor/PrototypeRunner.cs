using System;
using System.IO;

// Experimental synchronous comparison for the included sample only.
public static class PrototypeRunner
{
    public sealed class Result { public string Status; public string Path; }
    public static Result Run(string fixtureRoot, FixtureValidation.Fixture fixture, bool simulateRegression)
    {
        FixtureValidation.Validate(fixtureRoot, 1, new[] { fixture });
        var dir = Path.Combine(Path.GetTempPath(), "gdm001-prototype-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(dir);
        try
        {
            var copy = Path.Combine(dir, fixture.FileName);
            File.Copy(Path.Combine(fixtureRoot, fixture.FileName), copy);
            var state = SampleSaveLoader.Load(File.ReadAllText(copy), simulateRegression);
            return state.shield ? new Result { Status = "pass" } : new Result { Status = "regression", Path = "inventory.unique.shield_01" };
        }
        finally { Directory.Delete(dir, true); }
    }
}
