using System.Reflection.PortableExecutable;

internal static class PeParser
{
    const int MaxDirectoryBytes = 1024 * 1024;
    const int MaxNameBytes = 512;
    public sealed record Result(string machine, List<string> imports, List<string> delay_imports, string[] limitations);

    static string ReadName(PEReader pe, int nameRva)
    {
        if (nameRva <= 0) throw new InvalidDataException("Invalid import name RVA");
        PEMemoryBlock block = pe.GetSectionData(nameRva);
        var bytes = block.GetContent(0, Math.Min(block.Length, MaxNameBytes));
        int end = bytes.IndexOf((byte)0);
        if (end <= 0) throw new InvalidDataException("Unterminated or empty import name");
        var name = bytes.AsSpan(0, end);
        foreach (byte b in name)
            if (b < 0x20 || b > 0x7e || b == '/' || b == '\\' || b == ':')
                throw new InvalidDataException("Unsupported import name");
        return System.Text.Encoding.ASCII.GetString(name);
    }

    public static Result Inspect(Stream stream)
    {
        if (stream.Length > 64L * 1024 * 1024) throw new InvalidDataException("PE exceeds 64 MiB limit");
        using var pe = new PEReader(stream, PEStreamOptions.LeaveOpen);
        var headers = pe.PEHeaders;
        var optional = headers.PEHeader ?? throw new InvalidDataException("Missing PE optional header");
        var imports = new List<string>();
        var directory = optional.ImportTableDirectory;
        if (directory.RelativeVirtualAddress != 0 || directory.Size != 0)
        {
            if (directory.RelativeVirtualAddress <= 0 || directory.Size < 20 || directory.Size > MaxDirectoryBytes)
                throw new InvalidDataException("Invalid or oversized import directory");
            var data = pe.GetSectionData(directory.RelativeVirtualAddress).GetContent(0, directory.Size);
            bool terminated = false;
            for (int offset = 0; offset <= data.Length - 20; offset += 20)
            {
                var span = data.AsSpan(offset, 20);
                bool zero = true;
                foreach (byte value in span) if (value != 0) { zero = false; break; }
                if (zero) { terminated = true; break; }
                int nameRva = System.Buffers.Binary.BinaryPrimitives.ReadInt32LittleEndian(span.Slice(12, 4));
                imports.Add(ReadName(pe, nameRva));
            }
            if (!terminated) throw new InvalidDataException("Unterminated import directory");
        }
        var delayed = new List<string>();
        var delayDirectory = optional.DelayImportTableDirectory;
        if (delayDirectory.RelativeVirtualAddress != 0 || delayDirectory.Size != 0)
        {
            if (delayDirectory.RelativeVirtualAddress <= 0 || delayDirectory.Size < 32 || delayDirectory.Size > MaxDirectoryBytes)
                throw new InvalidDataException("Invalid or oversized delay-import directory");
            var data = pe.GetSectionData(delayDirectory.RelativeVirtualAddress).GetContent(0, delayDirectory.Size);
            bool terminated = false;
            for (int offset = 0; offset <= data.Length - 32; offset += 32)
            {
                var span = data.AsSpan(offset, 32);
                bool zero = true;
                foreach (byte value in span) if (value != 0) { zero = false; break; }
                if (zero) { terminated = true; break; }
                uint attributes = System.Buffers.Binary.BinaryPrimitives.ReadUInt32LittleEndian(span);
                if (attributes != 1) throw new InvalidDataException("Unsupported delay-import address form");
                int nameRva = System.Buffers.Binary.BinaryPrimitives.ReadInt32LittleEndian(span.Slice(4, 4));
                delayed.Add(ReadName(pe, nameRva));
            }
            if (!terminated) throw new InvalidDataException("Unterminated delay-import directory");
        }
        return new Result($"0x{(ushort)headers.CoffHeader.Machine:X4}", imports, delayed,
            new[] { "dynamic loads unknown", "ordinary and delay-import resolution not inspected" });
    }
}
