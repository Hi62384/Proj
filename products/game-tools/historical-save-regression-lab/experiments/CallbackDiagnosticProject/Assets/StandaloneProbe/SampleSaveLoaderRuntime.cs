using System;
using UnityEngine;

namespace SyntheticGameRuntime
{
// A fictional game's current loader. Inputs are synthetic and supplied by tests.
public static class SampleSaveLoader
{
    [Serializable] private class Save { public int version; public bool shield; public int potions; public bool questComplete; }
    public sealed class State { public bool shield; public int potions; public bool questComplete; }

    public static State Load(string json, bool introduceRegression = false)
    {
        var save = JsonUtility.FromJson<Save>(json);
        if (save == null || save.version < 1 || save.version > 3) throw new ArgumentException("Unsupported save version");
        return new State {
            shield = introduceRegression && save.version == 1 ? false : save.shield,
            potions = save.potions,
            questComplete = save.version >= 2 && save.questComplete
        };
    }
}

}
