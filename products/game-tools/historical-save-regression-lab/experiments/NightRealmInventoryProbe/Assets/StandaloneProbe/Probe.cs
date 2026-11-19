using System;
using System.IO;
using UnityEngine;
using Qanht.NightRealm.IOSystem;
namespace Qanht.NightRealm.EventManagers { public class ProbePlaceholder {} }
// Type-map placeholders are not NightRealm gameplay classes.
public interface IItem : Qanht.NightRealm.IOSystem.ISerializable {}
public abstract class DummySerialized : Qanht.NightRealm.IOSystem.SerializedObject { public override object Deserialize()=>null; public override Qanht.NightRealm.IOSystem.SerializedType GetSerializedType()=>Qanht.NightRealm.IOSystem.SerializedType.Null; }
public class Equipment { [Serializable] public class SerializedEquipment : DummySerialized {} }
public class SerializedResourceAsset : DummySerialized {}
namespace Qanht.NightRealm.AbilitySystem {
 public class PassiveAbility { [Serializable] public class PassiveAbilitySerialize : DummySerialized {} }
 public class OrientationAbility { [Serializable] public class SerializedOrientationAbility : DummySerialized {} }
 public class SelfActiveAbility { [Serializable] public class SerializedSeflActiveAbility : DummySerialized {} }
 public class TargetingAbility { [Serializable] public class SerializedTargetingAbility : DummySerialized {} }
}
public class EquipmentManager { [Serializable] public class SerializedEquipmentManager : DummySerialized {} }
public class SkillSet { [Serializable] public class SerializedSkillSet : DummySerialized {} }
// A synthetic item fills the real JsonHelper's consumable type slot.
public class ConsumableItem : IItem {
 public int count; public Qanht.NightRealm.IOSystem.SerializedObject Serialize()=>new SerializedConsumableItem { count=count };
 [Serializable] public class SerializedConsumableItem : Qanht.NightRealm.IOSystem.SerializedObject {
  public int count; public override object Deserialize()=>new ConsumableItem {count=count};
  public override Qanht.NightRealm.IOSystem.SerializedType GetSerializedType()=>Qanht.NightRealm.IOSystem.SerializedType.ConsumableItem;
 }
}
public static class NightRealmScratch {
 public static string Arg(string name) { var a=Environment.GetCommandLineArgs(); for(int i=0;i+1<a.Length;i++) if(a[i]==name) return a[i+1]; throw new ArgumentException(name); }
 public static string Root() { return Path.Combine(Path.GetDirectoryName(Arg("--synthetic-fixture")),"saves"); }
}
[Serializable] public class ProbeResult { public string status; public string path; public bool outsideWriteBlocked; public string outsideWriteError; public int count; public bool emptySlot; }
public static class NightRealmProbe {
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] public static void Run() {
  try {
   var root=NightRealmScratch.Root();Directory.CreateDirectory(root);FileNameData.CurrentUser="Synthetic";
   File.WriteAllText(NightRealmScratch.Arg("--synthetic-started"),"wrapped inventory");
   var items=ItemArray.GetIntance(new IItem[] { new ConsumableItem {count=3}, null });
   SaveLoadHandler.SaveToFile("Inventory",(Qanht.NightRealm.IOSystem.ISerializable)items);
   File.Copy(FileNameData.GetFullPath("Inventory"),FileNameData.GetFullPath("InventoryBefore"));
   var loaded=(ItemArray)SaveLoadHandler.LoadFromFile("Inventory");
   if(loaded==null || loaded.items==null || loaded.items.Length!=2) throw new Exception("inventory array mismatch");
   var item=loaded.items[0] as ConsumableItem;
   if(item==null || item.count!=3 || loaded.items[1]!=null) throw new Exception("inventory contents mismatch");
   string mode=NightRealmScratch.Arg("--synthetic-mode");if(mode=="regression") item.count=0;
   var r=new ProbeResult {status=item.count==3?"pass":"regression",path=item.count==3?"":"inventory.slot0.count",count=item.count,emptySlot=loaded.items[1]==null};
   SaveLoadHandler.SaveToFile("InventoryOut",(Qanht.NightRealm.IOSystem.ISerializable)loaded);
   try { File.WriteAllText(NightRealmScratch.Arg("--synthetic-canary"),"synthetic"); } catch(Exception e) {r.outsideWriteBlocked=true;r.outsideWriteError=e.GetType().Name;}
   File.WriteAllText(NightRealmScratch.Arg("--synthetic-result"),JsonUtility.ToJson(r));Application.Quit(r.status=="pass"?0:1);
  } catch(Exception e) {Debug.LogException(e);Application.Quit(2);}
 }
}
