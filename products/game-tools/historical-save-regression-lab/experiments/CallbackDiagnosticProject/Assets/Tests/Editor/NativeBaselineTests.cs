using NUnit.Framework;
using UnityEngine;

public class NativeBaselineTests
{
    [System.Serializable]
    private class SaveData
    {
        public int version;
        public bool hasShield;
    }

    [Test]
    public void NativeJsonAndAssertionsDetectLostInventory()
    {
        var saved = JsonUtility.FromJson<SaveData>("{\"version\":1,\"hasShield\":true}");
        Assert.That(saved.version, Is.EqualTo(1));
        Assert.That(saved.hasShield, Is.True, "inventory.unique.shield_01");
    }
}
