using System;
using System.Collections.Generic;
using System.Diagnostics;
public static class ManifestRunner { public sealed class Result { } }
public static class PrototypeReport { public static string SerializeSuite(IEnumerable<string> a,IEnumerable<ManifestRunner.Result> b,bool aborted) => throw new NotSupportedException(); public static bool ValidateCompleted(string json,IEnumerable<string> ids) => throw new NotSupportedException(); }
public static class StrictManifest { public static object ParseJson(string text) => throw new NotSupportedException(); }
public static class Program
{
    public static void Main(string[] args)
    {
        if(args.Length!=1) throw new ArgumentException("report root required");
        var journal=PrototypeRunJournal.Begin(args[0]);
        Console.WriteLine(journal.DirectoryPath); Console.Out.Flush();
        Process.GetCurrentProcess().Kill();
    }
}
