using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

// Prototype contract: one direct child file and explicit boolean observations.
// Reject unknown fields so extending this format requires a new schema version.
public static class StrictManifest
{
    public sealed class Suite { public string Id; public List<Fixture> Fixtures; }
    public sealed class Fixture { public string Id, File, Hash; public List<Assertion> Assertions; }
    public sealed class Assertion { public string Path; public bool Expected; }

    public static Suite Parse(string json)
    {
        var root = Obj(new Json(json).Read(), "manifest", "schema_version", "suite_id", "fixtures");
        if (!(root["schema_version"] is double version) || version != 1) throw Error("Unsupported schema_version");
        var suite = new Suite { Id = Str(root["suite_id"]), Fixtures = new List<Fixture>() };
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var item in Arr(root["fixtures"]))
        {
            var o = Obj(item, "fixture", "fixture_id", "file", "sha256", "assertions");
            var f = new Fixture { Id = Str(o["fixture_id"]), File = Str(o["file"]), Hash = Str(o["sha256"]), Assertions = new List<Assertion>() };
            if (!ids.Add(f.Id)) throw Error("Duplicate fixture_id");
            if (f.File == "." || f.File == ".." || f.File.IndexOfAny(new[] { '/', '\\', ':' }) >= 0 || Path.GetFileName(f.File) != f.File) throw Error("Unsafe file");
            if (f.Hash.Length != 64 || f.Hash.Any(c => !Uri.IsHexDigit(c))) throw Error("Invalid sha256");
            var paths = new HashSet<string>(StringComparer.Ordinal);
            foreach (var a in Arr(o["assertions"]))
            {
                var entry = Obj(a, "assertion", "path", "type", "equals");
                var path = Str(entry["path"]);
                if (!paths.Add(path) || Str(entry["type"]) != "boolean" || !(entry["equals"] is bool expected)) throw Error("Invalid assertion");
                f.Assertions.Add(new Assertion { Path = path, Expected = expected });
            }
            if (f.Assertions.Count == 0) throw Error("Empty assertions");
            suite.Fixtures.Add(f);
        }
        if (suite.Fixtures.Count == 0) throw Error("Empty fixtures");
        return suite;
    }
    private static ArgumentException Error(string message) => new ArgumentException(message);
    private static string Str(object v) { if (!(v is string s) || String.IsNullOrWhiteSpace(s)) throw Error("Expected non-empty string"); return s; }
    private static List<object> Arr(object v) => v as List<object> ?? throw Error("Expected array");
    private static Dictionary<string, object> Obj(object v, string name, params string[] keys)
    {
        var o = v as Dictionary<string, object> ?? throw Error("Expected " + name + " object");
        if (o.Count != keys.Length || keys.Any(k => !o.ContainsKey(k))) throw Error("Missing or unknown " + name + " field");
        return o;
    }

    // Bounded recursive-descent JSON parser. Rejects duplicate keys, non-JSON numbers,
    // trailing content, malformed escapes, and excessive input/depth.
    private sealed class Json
    {
        readonly string s; int i;
        public Json(string text) { s = text ?? throw Error("Missing JSON"); if (s.Length > 1048576) throw Error("Manifest too large"); }
        void Ws() { while (i < s.Length && (s[i] == ' ' || s[i] == '\t' || s[i] == '\r' || s[i] == '\n')) i++; }
        bool Take(char c) { Ws(); if (i < s.Length && s[i] == c) { i++; return true; } return false; }
        void Need(char c) { if (!Take(c)) throw Error("Invalid JSON at " + i); }
        public object Read() { var v = Value(0); Ws(); if (i != s.Length) throw Error("Trailing JSON at " + i); return v; }
        object Value(int depth)
        {
            if (depth > 32) throw Error("JSON too deep"); Ws(); if (i == s.Length) throw Error("Unexpected end");
            if (s[i] == '"') return StringValue();
            if (Take('{')) { var o = new Dictionary<string, object>(StringComparer.Ordinal); if (Take('}')) return o; do { Ws(); if (i == s.Length || s[i] != '"') throw Error("Expected key"); var k = StringValue(); Need(':'); var v = Value(depth + 1); if (o.ContainsKey(k)) throw Error("Duplicate key: " + k); o.Add(k, v); } while (Take(',')); Need('}'); return o; }
            if (Take('[')) { var a = new List<object>(); if (Take(']')) return a; do { a.Add(Value(depth + 1)); } while (Take(',')); Need(']'); return a; }
            foreach (var lit in new[] { "true", "false", "null" }) if (s.Length - i >= lit.Length && String.CompareOrdinal(s, i, lit, 0, lit.Length) == 0) { i += lit.Length; return lit == "null" ? null : (object)(lit == "true"); }
            int start = i; if (i < s.Length && s[i] == '-') i++; if (i == s.Length || s[i] < '0' || s[i] > '9') throw Error("Invalid number");
            if (s[i++] != '0') while (i < s.Length && s[i] >= '0' && s[i] <= '9') i++;
            if (i < s.Length && s[i] == '.') { i++; int p = i; while (i < s.Length && s[i] >= '0' && s[i] <= '9') i++; if (p == i) throw Error("Invalid fraction"); }
            if (i < s.Length && (s[i] == 'e' || s[i] == 'E')) { i++; if (i < s.Length && (s[i] == '+' || s[i] == '-')) i++; int p = i; while (i < s.Length && s[i] >= '0' && s[i] <= '9') i++; if (p == i) throw Error("Invalid exponent"); }
            if (!Double.TryParse(s.Substring(start, i - start), NumberStyles.Float, CultureInfo.InvariantCulture, out var n) || Double.IsInfinity(n) || Double.IsNaN(n)) throw Error("Invalid number"); return n;
        }
        string StringValue()
        {
            Need('"'); var b = new StringBuilder();
            while (i < s.Length) { char c = s[i++]; if (c == '"') return b.ToString(); if (c < 32) throw Error("Control character"); if (c != '\\') { b.Append(c); continue; } if (i == s.Length) throw Error("Invalid escape"); c = s[i++];
                switch (c) { case '"': case '\\': case '/': b.Append(c); break; case 'b': b.Append('\b'); break; case 'f': b.Append('\f'); break; case 'n': b.Append('\n'); break; case 'r': b.Append('\r'); break; case 't': b.Append('\t'); break; case 'u': if (i + 4 > s.Length || !UInt16.TryParse(s.Substring(i, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture, out var code)) throw Error("Invalid unicode escape"); b.Append((char)code); i += 4; break; default: throw Error("Invalid escape"); }
            } throw Error("Unterminated string");
        }
    }
}
