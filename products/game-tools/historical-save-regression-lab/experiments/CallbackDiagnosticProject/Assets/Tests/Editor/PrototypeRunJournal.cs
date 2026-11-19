using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

// Synthetic-only journal. Not an OS sandbox or a durability guarantee.
// Readers must consider a run incomplete unless complete.json exists and is valid.
public sealed class PrototypeRunJournal
{
    public string DirectoryPath { get; private set; }
    public string IncompletePath => Path.Combine(DirectoryPath,"incomplete.json");
    public string CompletePath => Path.Combine(DirectoryPath,"complete.json");
    private PrototypeRunJournal() { }
    public static PrototypeRunJournal Begin(string root)
    {
        if (String.IsNullOrWhiteSpace(root) || !Directory.Exists(root)) throw new ArgumentException("Existing report root required");
        var path=Path.Combine(Path.GetFullPath(root),"gdm-run-"+Guid.NewGuid().ToString("N"));
        if (Directory.Exists(path)) throw new IOException("Run path already exists");
        Directory.CreateDirectory(path);
        var journal=new PrototypeRunJournal { DirectoryPath=path };
        WriteNew(journal.IncompletePath,"{\"schema_version\":1,\"state\":\"incomplete\",\"success\":false}");
        return journal;
    }
    public void Complete(IEnumerable<string> expected, IEnumerable<ManifestRunner.Result> results)
    {
        // Validate the entire report before publishing a final filename.
        var json=PrototypeReport.SerializeSuite(expected,results,false);
        var temporary=Path.Combine(DirectoryPath,"report-"+Guid.NewGuid().ToString("N")+".tmp");
        try { WriteNew(temporary,json); File.Move(temporary,CompletePath); }
        finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }
    // Fail closed: partial files never count as success and corrupt final files
    // do not fall back to an older marker. Inputs are trusted synthetic paths.
    public static string Inspect(string directory, IEnumerable<string> expected)
    {
        if (String.IsNullOrWhiteSpace(directory) || expected == null) throw new ArgumentNullException();
        try
        {
            var complete=Path.Combine(directory,"complete.json");
            if (File.Exists(complete)) return PrototypeReport.ValidateCompleted(ReadBounded(complete),expected) ? "complete_pass" : "complete_fail";
            var marker=Path.Combine(directory,"incomplete.json");
            if (!File.Exists(marker)) return "invalid";
            var obj=StrictManifest.ParseJson(ReadBounded(marker)) as Dictionary<string,object>;
            if (obj == null || obj.Count != 3 || !obj.ContainsKey("schema_version") || !obj.ContainsKey("state") || !obj.ContainsKey("success") || !(obj["schema_version"] is double v) || v != 1 || !(obj["state"] is string state) || state != "incomplete" || !(obj["success"] is bool success) || success) return "invalid";
            return "incomplete";
        }
        catch (Exception e) when (e is IOException || e is UnauthorizedAccessException || e is ArgumentException || e is NotSupportedException) { return "invalid"; }
    }
    private static string ReadBounded(string path)
    {
        using (var input=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.Read))
        {
            if (input.Length > 1024*1024) throw new ArgumentException("Report too large");
            using (var reader=new StreamReader(input,new UTF8Encoding(false,true),true)) return reader.ReadToEnd();
        }
    }
    private static void WriteNew(string path,string text)
    {
        var bytes=new UTF8Encoding(false).GetBytes(text);
        using (var stream=new FileStream(path,FileMode.CreateNew,FileAccess.Write,FileShare.None))
        { stream.Write(bytes,0,bytes.Length); stream.Flush(true); }
    }
}
