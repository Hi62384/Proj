using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class StandaloneProbeBuild
{
    public static void Build()
    {
        var output=Environment.GetEnvironmentVariable("GDM001_PLAYER_OUTPUT");
        if(String.IsNullOrWhiteSpace(output)||File.Exists(output)) throw new ArgumentException("Fresh output path required");
        var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        if(!EditorSceneManager.SaveScene(scene,"Assets/StandaloneProbe/SyntheticProbe.unity")) throw new IOException("Scene save failed");
        var report=BuildPipeline.BuildPlayer(new[]{"Assets/StandaloneProbe/SyntheticProbe.unity"},output,BuildTarget.StandaloneWindows64,BuildOptions.None);
        Debug.Log("Synthetic standalone build result="+report.summary.result);
        EditorApplication.Exit(report.summary.result==BuildResult.Succeeded?0:1);
    }
}
