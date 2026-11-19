using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;

// Deliberately demonstrates that a copied fixture does not confine an adapter.
// This controlled canary touches only its own disposable temporary directory.
public class AdapterEscapeCanaryTests
{
    private sealed class EscapeAdapter : IAsyncSaveAdapter
    {
        private readonly string canary; private readonly string root;
        public EscapeAdapter(string root,string canary) { this.root=root;this.canary=canary; }
        public Task ResetAsync(CancellationToken c) => Task.CompletedTask;
        public Task RestoreAsync(string fixture,CancellationToken c)
        {
            var scratch=Path.GetFullPath(Path.GetDirectoryName(fixture)).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar;
            if(Path.GetFullPath(canary).StartsWith(scratch,StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Canary must be outside fixture copy");
            if(!Path.GetFullPath(canary).StartsWith(Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Canary must be inside test root");
            File.WriteAllText(canary,"synthetic external write");return Task.CompletedTask;
        }
        public Task<IReadOnlyDictionary<string,object>> CaptureAsync(CancellationToken c) => Task.FromResult<IReadOnlyDictionary<string,object>>(new Dictionary<string,object>{{"shield",true}});
    }
    [Test] public async Task FixtureCopyDoesNotEnforceAdapterWriteBoundary()
    {
        var root=Path.Combine(Path.GetTempPath(),"gdm-escape-test-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(root);
        var canary=Path.Combine(root,"outside-fixture-copy.txt");
        try
        {
            var fixture=new StrictManifest.Fixture{Id="v1",File="v1.json",Hash="462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc",Assertions=new List<StrictManifest.Assertion>{new StrictManifest.Assertion{Path="shield",Expected=true}}};
            var result=await ManifestRunner.RunAsync(Path.Combine(Application.dataPath,"Tests","Fixtures"),Path.GetTempPath(),fixture,new EscapeAdapter(root,canary),CancellationToken.None);
            Assert.That(result.Status,Is.EqualTo("pass"));Assert.That(File.ReadAllText(canary),Is.EqualTo("synthetic external write"));
        }
        finally { Directory.Delete(root,true); }
    }
}
