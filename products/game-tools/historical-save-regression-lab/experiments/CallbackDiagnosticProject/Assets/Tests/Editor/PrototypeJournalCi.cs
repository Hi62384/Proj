using System.Collections.Generic;

// Prototype mapping for a caller that controls process exit. Does not launch Unity.
public static class PrototypeJournalCi
{
    public static int ExitCode(string directory, IEnumerable<string> expectedIds) =>
        PrototypeRunJournal.Inspect(directory,expectedIds) == "complete_pass" ? 0 : 1;
}
