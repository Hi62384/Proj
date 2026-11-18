using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;

// Internal prototype; paths are deliberately limited to one file directly in the fixture root.
public static class FixtureValidation
{
    public sealed class Fixture { public string Id; public string FileName; public string Sha256; }

    public static void Validate(string root, int schemaVersion, IEnumerable<Fixture> fixtures)
    {
        if (schemaVersion != 1 || fixtures == null) throw new ArgumentException("Unsupported schema or missing fixtures");
        var rootInfo = new DirectoryInfo(Path.GetFullPath(root));
        if (!rootInfo.Exists || (rootInfo.Attributes & FileAttributes.ReparsePoint) != 0) throw new ArgumentException("Invalid fixture root");
        var ids = new HashSet<string>(StringComparer.Ordinal);
        var count = 0;
        foreach (var fixture in fixtures)
        {
            count++;
            if (fixture == null || String.IsNullOrWhiteSpace(fixture.Id) || !ids.Add(fixture.Id)) throw new ArgumentException("Missing or duplicate ID");
            var name = fixture.FileName;
            if (String.IsNullOrWhiteSpace(name) || name == "." || name == ".." || name.IndexOfAny(new[] { '/', '\\', ':' }) >= 0 || Path.GetFileName(name) != name) throw new ArgumentException("Unsafe fixture path");
            if (fixture.Sha256 == null || fixture.Sha256.Length != 64 || fixture.Sha256.Any(c => !Uri.IsHexDigit(c))) throw new ArgumentException("Invalid hash");
            var file = new FileInfo(Path.Combine(rootInfo.FullName, name));
            if (!file.Exists || (file.Attributes & FileAttributes.ReparsePoint) != 0) throw new ArgumentException("Missing or linked fixture");
            using (var sha = SHA256.Create()) using (var stream = file.OpenRead())
            {
                var hash = BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "");
                if (!String.Equals(hash, fixture.Sha256, StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("Fixture hash mismatch");
            }
        }
        if (count == 0) throw new ArgumentException("Empty fixture list");
    }
}
