using System;
using System.IO;
using UnityEngine;
using Qanht.NightRealm.IOSystem;
namespace Qanht.NightRealm.EventManagers {
 public static class EventManager { public static void AddListener(string n,Action a){} public static void RemoveListener(string n,Action a){} }
 public static class EventManager<T> { public static void AddListener(string n,Action<T> a){} public static void RemoveListener(string n,Action<T> a){} }
}
namespace Qanht.NightRealm.AudioManagement { public static class AudioManager { public static void Play(string n){} } }
namespace Qanht.NightRealm.ObjectPooling { public class Prefab {} public class PoolObject : MonoBehaviour {} public static class PoolManager { public static bool Get<T>(Prefab p,out T instance) where T:class { instance=null;return false; } } }
public class Stat {} public class StatModifier {}
public class Stats { public void RemoveModifier(Stat s,StatModifier m){} public void ApplyModifier(Stat s,StatModifier m){} }
public class ResourceValue { public void Fill(){} }
public class Fighter : MonoBehaviour { public Stats Stats=new Stats(); public ResourceValue Health=new ResourceValue(); public ResourceValue Mana=new ResourceValue(); public Vector3 Position=>Vector3.zero; }
public class GrowingStat { public System.Collections.Generic.Dictionary<Stat,StatModifier> GetGrowingStat(int level) => new System.Collections.Generic.Dictionary<Stat,StatModifier>(); }
public class BaseStatData : ScriptableObject { public GrowingStat growStat=new GrowingStat(); }

namespace Qanht.NightRealm.IOSystem {
 // Stubs for unused wrapped-object overloads. This probe exercises only generic JSON.
 public interface ISerializable {}
 public static class JsonHelper { public static string ToWrappedJson(this ISerializable x) { throw new NotSupportedException(); } public static object WrappedJsonToObject(string x) { throw new NotSupportedException(); } }
}
public static class NightRealmScratch {
 public static string Arg(string name) { var a=Environment.GetCommandLineArgs(); for(int i=0;i+1<a.Length;i++) if(a[i]==name) return a[i+1]; throw new ArgumentException(name); }
 public static string Root() { return Path.Combine(Path.GetDirectoryName(Arg("--synthetic-fixture")),"saves"); }
}
[Serializable] public class ProbeResult { public string status; public string path; public bool outsideWriteBlocked; public string outsideWriteError; public int restoredXp; }
public static class NightRealmProbe {
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
 public static void Run() {
  try {
   string root=NightRealmScratch.Root(); Directory.CreateDirectory(root); FileNameData.CurrentUser="Synthetic";
   string result=NightRealmScratch.Arg("--synthetic-result");string mode=NightRealmScratch.Arg("--synthetic-mode");
   File.WriteAllText(NightRealmScratch.Arg("--synthetic-started"),"component restore");
   File.WriteAllText(FileNameData.GetFullPath("GameStatus"),"{\"hasGuided\":true,\"gold\":123}");
   string levelFile=FileNameData.GetFullPath("PlayerLevel");
   File.WriteAllText(levelFile,"{\"currentLevel\":2,\"currentXp\":7,\"capacityXp\":100}");
   File.Copy(levelFile,FileNameData.GetFullPath("PlayerLevelBefore"));
   var obj=new GameObject("SyntheticLevelComponent"); obj.SetActive(false);
   var player=obj.AddComponent<Fighter>(); var level=obj.AddComponent<PlayerLevelSystem>();
   var flags=System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance;
   typeof(PlayerLevelSystem).GetField("player",flags).SetValue(level,player);
   typeof(PlayerLevelSystem).GetField("statData",flags).SetValue(level,ScriptableObject.CreateInstance<BaseStatData>());
   obj.SetActive(true);
   if(PlayerLevelSystem.CurrentLevel!=2 || PlayerLevelSystem.CurrentXp!=7 || PlayerLevelSystem.CapacityXp!=100) throw new Exception("initial restore mismatch");
   var r=new ProbeResult {status="pass",path="",restoredXp=PlayerLevelSystem.CurrentXp};
   if(mode=="regression") {
    level.SaveToFile();level.LoadFromFile();r.restoredXp=PlayerLevelSystem.CurrentXp;
    if(r.restoredXp!=7) { r.status="regression";r.path="player.currentXp"; }
   }
   try { File.WriteAllText(NightRealmScratch.Arg("--synthetic-canary"),"synthetic"); } catch(Exception e) { r.outsideWriteBlocked=true;r.outsideWriteError=e.GetType().Name; }
   File.WriteAllText(result,JsonUtility.ToJson(r)); Application.Quit(r.status=="pass"?0:1);
  } catch(Exception e) { Debug.LogException(e);Application.Quit(2); }
 }
}
