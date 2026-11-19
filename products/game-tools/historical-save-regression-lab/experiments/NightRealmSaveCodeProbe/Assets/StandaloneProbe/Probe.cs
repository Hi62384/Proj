using System;
using System.IO;
using UnityEngine;
using Qanht.NightRealm.IOSystem;
namespace Qanht.NightRealm.EventManagers { public class ProbePlaceholder {} }
namespace Qanht.NightRealm.IOSystem {
 // Stubs for unused wrapped-object overloads. This probe exercises only generic JSON.
 public interface ISerializable {}
 public static class JsonHelper { public static string ToWrappedJson(this ISerializable x) { throw new NotSupportedException(); } public static object WrappedJsonToObject(string x) { throw new NotSupportedException(); } }
}
public static class NightRealmScratch {
 public static string Arg(string name) { var a=Environment.GetCommandLineArgs(); for(int i=0;i+1<a.Length;i++) if(a[i]==name) return a[i+1]; throw new ArgumentException(name); }
 public static string Root() { return Path.Combine(Path.GetDirectoryName(Arg("--synthetic-fixture")),"saves"); }
}
// Synthetic DTOs mirror two NightRealm fields, not its game components.
[Serializable] public class GameStatus { public bool hasGuided; public int gold; }
[Serializable] public class LevelData { public int currentLevel; public int currentXp; public int capacityXp; }
[Serializable] public class ProbeResult { public string status; public string path; public bool outsideWriteBlocked; public string outsideWriteError; }
public static class NightRealmProbe {
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
 public static void Run() {
  try {
   string root=NightRealmScratch.Root(); Directory.CreateDirectory(root); FileNameData.CurrentUser="Synthetic";
   string result=NightRealmScratch.Arg("--synthetic-result"); string started=NightRealmScratch.Arg("--synthetic-started");
   File.WriteAllText(started,"generic handler roundtrip");
   File.WriteAllText(FileNameData.GetFullPath("GameStatus"),"{\"hasGuided\":true,\"gold\":123}");
   File.WriteAllText(FileNameData.GetFullPath("PlayerLevel"),"{\"currentLevel\":2,\"currentXp\":7,\"capacityXp\":100}");
   var g=SaveLoadHandler.LoadFromFile<GameStatus>("GameStatus"); var l=SaveLoadHandler.LoadFromFile<LevelData>("PlayerLevel");
   if(g==null || l==null || !g.hasGuided || g.gold!=123 || l.currentLevel!=2 || l.currentXp!=7 || l.capacityXp!=100) throw new Exception("load mismatch");
   SaveLoadHandler.SaveToFile("GameStatusOut",(object)g); SaveLoadHandler.SaveToFile("PlayerLevelOut",(object)l);
   var g2=SaveLoadHandler.LoadFromFile<GameStatus>("GameStatusOut"); var l2=SaveLoadHandler.LoadFromFile<LevelData>("PlayerLevelOut");
   if(g2==null || l2==null || g2.gold!=123 || l2.currentXp!=7) throw new Exception("roundtrip mismatch");
   var r=new ProbeResult {status="pass",path=""};
   try { File.WriteAllText(NightRealmScratch.Arg("--synthetic-canary"),"synthetic"); } catch(Exception e) { r.outsideWriteBlocked=true;r.outsideWriteError=e.GetType().Name; }
   File.WriteAllText(result,JsonUtility.ToJson(r)); Application.Quit(0);
  } catch(Exception e) { Debug.LogException(e);Application.Quit(1); }
 }
}
