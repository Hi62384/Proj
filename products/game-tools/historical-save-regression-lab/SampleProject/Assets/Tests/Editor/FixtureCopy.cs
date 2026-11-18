using System;
using System.IO;
using System.Security.Cryptography;

// A disposable copy, not an operating-system security sandbox. Use only with
// trusted adapters which redirect all game writes to their supplied directory.
public sealed class FixtureCopy : IDisposable
{
    public string DirectoryPath { get; private set; }
    public string FilePath { get; private set; }
    private FixtureCopy() { }

    public static FixtureCopy Create(string sourceRoot, StrictManifest.Fixture fixture, string scratchRoot)
    {
        if (fixture == null) throw new ArgumentNullException(nameof(fixture));
        // Validate again: public model objects can be modified after parsing.
        var name = fixture.File;
        if (String.IsNullOrWhiteSpace(name) || name == "." || name == ".." || name.IndexOfAny(new[] { '/', '\\', ':' }) >= 0 || Path.GetFileName(name) != name) throw new ArgumentException("Unsafe file");
        var root = Path.GetFullPath(sourceRoot);
        var scratch = Path.GetFullPath(scratchRoot);
        if (String.Equals(root.TrimEnd(Path.DirectorySeparatorChar), scratch.TrimEnd(Path.DirectorySeparatorChar), StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("Scratch must differ from source");
        RejectLinks(root); RejectLinks(scratch);
        var source = Path.Combine(root, name);
        RejectLinks(source);
        // Hash the exact bytes copied, with a size limit. Never open the source for writing.
        byte[] bytes;
        using (var stream = new FileStream(source, FileMode.Open, FileAccess.Read, FileShare.Read))
        {
            if (stream.Length > 32 * 1024 * 1024) throw new ArgumentException("Fixture too large");
            using (var buffer = new MemoryStream()) { stream.CopyTo(buffer); bytes = buffer.ToArray(); }
        }
        using (var sha = SHA256.Create())
        {
            var hash = BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "");
            if (!String.Equals(hash, fixture.Hash, StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("Fixture hash mismatch");
        }
        var copy = new FixtureCopy { DirectoryPath = Path.Combine(scratch, "gdm001-" + Guid.NewGuid().ToString("N")) };
        Directory.CreateDirectory(copy.DirectoryPath);
        try
        {
            copy.FilePath = Path.Combine(copy.DirectoryPath, name);
            using (var output = new FileStream(copy.FilePath, FileMode.CreateNew, FileAccess.Write, FileShare.None)) output.Write(bytes, 0, bytes.Length);
            return copy;
        }
        catch { copy.Dispose(); throw; }
    }
    private static void RejectLinks(string path)
    {
        var full = Path.GetFullPath(path);
        for (var part = full; !String.IsNullOrEmpty(part); part = Path.GetDirectoryName(part))
        {
            if ((File.GetAttributes(part) & FileAttributes.ReparsePoint) != 0) throw new ArgumentException("Linked path unsupported");
            var parent = Path.GetDirectoryName(part);
            if (String.Equals(parent, part, StringComparison.OrdinalIgnoreCase)) break;
        }
    }
    public void Dispose()
    {
        if (DirectoryPath == null) return;
        // Do not follow a replaced sandbox directory during cleanup.
        if (Directory.Exists(DirectoryPath))
        {
            if ((File.GetAttributes(DirectoryPath) & FileAttributes.ReparsePoint) != 0) throw new IOException("Sandbox was replaced by a link");
            Directory.Delete(DirectoryPath, true);
        }
        DirectoryPath = null; FilePath = null;
    }
}
