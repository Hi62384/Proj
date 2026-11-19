using System.Text.Json;

// Feasibility probe only. It inspects one PE file; it is not a package verifier.
if (args.Length != 1)
{
    Console.Error.WriteLine("usage: PeProbe <pe-file>");
    return 2;
}
try
{
    using var stream = new FileStream(args[0], FileMode.Open, FileAccess.Read, FileShare.Read);
    Console.WriteLine(JsonSerializer.Serialize(PeParser.Inspect(stream)));
    return 0;
}
catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or BadImageFormatException
                           or InvalidDataException or ArgumentException or OverflowException)
{
    Console.Error.WriteLine($"Cannot inspect PE: {ex.Message}");
    return 2;
}
