using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEditor;
using UnityEngine;

// Synthetic experiments only. Never use this entry point for real saves.
public static class PrototypeJournalEntryPoint
{
    private sealed class SampleAdapter : IAsyncSaveAdapter
    {
        private readonly bool fault; private SampleSaveLoader.State state;
        public SampleAdapter(bool fault) { this.fault=fault; }
        public Task ResetAsync(CancellationToken c) { state=null; return Task.CompletedTask; }
        public async Task RestoreAsync(string path,CancellationToken c) { await Task.Yield(); state=SampleSaveLoader.Load(File.ReadAllText(path),fault); }
        public Task<IReadOnlyDictionary<string,object>> CaptureAsync(CancellationToken c) => Task.FromResult<IReadOnlyDictionary<string,object>>(new Dictionary<string,object>{{"shield",state.shield},{"potions",state.potions},{"questComplete",state.questComplete}});
    }
    public static void InspectAndExit()
    {
        var directory=Environment.GetEnvironmentVariable("GDM001_JOURNAL_PATH");
        var id=Environment.GetEnvironmentVariable("GDM001_EXPECTED_ID");
        var code=1;
        try { if (!String.IsNullOrWhiteSpace(directory) && !String.IsNullOrWhiteSpace(id)) code=PrototypeJournalCi.ExitCode(directory,new[]{id}); }
        catch (Exception) { code=1; }
        Debug.Log("Synthetic journal check exit="+code); EditorApplication.Exit(code);
    }
    public static void RunSyntheticAndExit()
    {
        EditorApplication.delayCall += async () => {
            var code=1;
            try
            {
                var root=Environment.GetEnvironmentVariable("GDM001_JOURNAL_ROOT");
                var mode=Environment.GetEnvironmentVariable("GDM001_SYNTHETIC_MODE");
                if (String.IsNullOrWhiteSpace(root) || (mode!="pass" && mode!="regression")) throw new ArgumentException();
                var fixture=new StrictManifest.Fixture { Id="fixture",File="v1.json",Hash="462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc",Assertions=new List<StrictManifest.Assertion> { new StrictManifest.Assertion { Path="shield",Expected=true } } };
                var journal=PrototypeRunJournal.Begin(root);
                Debug.Log("Synthetic journal directory="+journal.DirectoryPath);
                await PrototypeSuite.RunRecordedAsync(Path.Combine(Application.dataPath,"Tests","Fixtures"),Path.GetTempPath(),new[]{fixture},f=>new SampleAdapter(mode=="regression"),TimeSpan.FromSeconds(30),CancellationToken.None,journal);
                code=PrototypeJournalCi.ExitCode(journal.DirectoryPath,new[]{"fixture"});
            }
            catch (Exception error) { Debug.LogError("Synthetic runner failed: "+error.GetType().Name); }
            Debug.Log("Synthetic suite exit="+code); EditorApplication.Exit(code);
        };
    }

    public static void RunManifestAndExit()
    {
        EditorApplication.delayCall += async () => {
            var code=1;
            try
            {
                var root=Environment.GetEnvironmentVariable("GDM001_JOURNAL_ROOT");
                var manifestPath=Environment.GetEnvironmentVariable("GDM001_MANIFEST_PATH");
                var mode=Environment.GetEnvironmentVariable("GDM001_SYNTHETIC_MODE");
                if (String.IsNullOrWhiteSpace(root) || String.IsNullOrWhiteSpace(manifestPath) || (mode!="pass" && mode!="regression")) throw new ArgumentException();
                var journal=PrototypeRunJournal.Begin(root);
                Debug.Log("Synthetic manifest journal="+journal.DirectoryPath);
                string text;
                using (var stream=new FileStream(manifestPath,FileMode.Open,FileAccess.Read,FileShare.Read))
                {
                    if (stream.Length>1024*1024) throw new ArgumentException("Manifest too large");
                    using (var reader=new StreamReader(stream,new UTF8Encoding(false,true),true)) text=reader.ReadToEnd();
                }
                var suite=StrictManifest.Parse(text); var ids=suite.Fixtures.Select(f=>f.Id).ToArray();
                await PrototypeSuite.RunRecordedAsync(Path.Combine(Application.dataPath,"Tests","Fixtures"),Path.GetTempPath(),suite.Fixtures,f=>new SampleAdapter(mode=="regression"),TimeSpan.FromSeconds(30),CancellationToken.None,journal);
                code=PrototypeJournalCi.ExitCode(journal.DirectoryPath,ids);
            }
            catch (Exception error) { Debug.LogError("Synthetic manifest run failed: "+error.GetType().Name); }
            Debug.Log("Synthetic manifest suite exit="+code); EditorApplication.Exit(code);
        };
    }
}
