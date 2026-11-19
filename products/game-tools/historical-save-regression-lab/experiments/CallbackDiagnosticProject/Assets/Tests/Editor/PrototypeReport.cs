using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

// Experimental in-memory output. Caller must supply the intended fixture IDs.
// This does not persist progress or detect process crashes on its own.
public static class PrototypeReport
{
    [Serializable] private sealed class Item { public string fixture_id; public string status; public string path; }
    [Serializable] private sealed class Report { public int schema_version = 1; public string state; public bool success; public int expected_count; public int completed_count; public Item[] results; }
    public static string SerializeSuite(IEnumerable<string> expectedIds, IEnumerable<ManifestRunner.Result> source, bool aborted)
    {
        if (expectedIds == null || source == null) throw new ArgumentNullException();
        var expected = expectedIds.ToArray();
        if (expected.Length == 0 || expected.Any(String.IsNullOrWhiteSpace) || expected.Distinct(StringComparer.Ordinal).Count() != expected.Length)
            throw new ArgumentException("Invalid expected fixture ids");
        var allowed = new HashSet<string>(expected, StringComparer.Ordinal);
        var seen = new HashSet<string>(StringComparer.Ordinal);
        var items = new List<Item>();
        foreach (var result in source)
        {
            if (result == null || String.IsNullOrWhiteSpace(result.FixtureId) || !allowed.Contains(result.FixtureId) || !seen.Add(result.FixtureId)) throw new ArgumentException("Invalid or duplicate fixture id");
            if (result.Status != "pass" && result.Status != "regression" && result.Status != "invalid_fixture" && result.Status != "adapter_error" && result.Status != "runner_error" && result.Status != "timeout") throw new ArgumentException("Unsupported outcome");
            if (result.Status != "regression" && result.Path != null) throw new ArgumentException("Only regressions may contain a path");
            if (result.Status == "regression" && String.IsNullOrWhiteSpace(result.Path)) throw new ArgumentException("Regression requires a path");
            items.Add(new Item { fixture_id = result.FixtureId, status = result.Status, path = result.Path });
        }
        if (!aborted && seen.Count != expected.Length) throw new ArgumentException("Completed report is missing fixture outcomes");
        var ordered = items.OrderBy(x => x.fixture_id, StringComparer.Ordinal).ToArray();
        return JsonUtility.ToJson(new Report { state = aborted ? "aborted" : "complete", success = !aborted && ordered.All(x => x.status == "pass"), expected_count = expected.Length, completed_count = ordered.Length, results = ordered });
    }
    // Revalidate an on-disk report against caller-owned expected IDs; never trust
    // the stored success flag or counts in isolation.
    internal static bool ValidateCompleted(string json, IEnumerable<string> expectedIds)
    {
        var expected = expectedIds.ToArray();
        var obj = StrictManifest.ParseJson(json) as Dictionary<string, object>;
        if (obj == null || obj.Count != 6 || !new[] { "schema_version", "state", "success", "expected_count", "completed_count", "results" }.All(obj.ContainsKey)) throw new ArgumentException("Invalid report fields");
        if (!(obj["schema_version"] is double schema) || schema != 1 || !(obj["state"] is string state) || state != "complete" || !(obj["success"] is bool declared) || !(obj["expected_count"] is double ec) || ec != expected.Length || !(obj["completed_count"] is double cc) || cc != expected.Length) throw new ArgumentException("Invalid report metadata");
        var entries = obj["results"] as List<object> ?? throw new ArgumentException("Invalid report results");
        var results = new List<ManifestRunner.Result>();
        foreach (var entry in entries)
        {
            var item = entry as Dictionary<string, object>;
            if (item == null || item.Count != 3 || !item.ContainsKey("fixture_id") || !item.ContainsKey("status") || !item.ContainsKey("path") || !(item["fixture_id"] is string id) || !(item["status"] is string status)) throw new ArgumentException("Invalid report item");
            if (item["path"] != null && !(item["path"] is string)) throw new ArgumentException("Invalid report path");
            var path = item["path"] as string;
            if (status != "regression" && path == "") path = null; // Unity serializes null strings as empty.
            results.Add(new ManifestRunner.Result { FixtureId=id, Status=status, Path=path });
        }
        SerializeSuite(expected,results,false); // validates identifiers, count and outcomes
        var computed = results.All(x => x.Status == "pass");
        if (declared != computed) throw new ArgumentException("Contradictory success flag");
        return computed;
    }
}
