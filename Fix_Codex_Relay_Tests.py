"""Update one outdated Codex Relay unit-test assertion for permission profiles.

Run from the Proj repository root after Fix_Codex_Relay_Permissions.py:
    python Fix_Codex_Relay_Tests.py
    python -m unittest discover -s portfolio_autopilot/codex_relay/tests -v

This changes only portfolio_autopilot/codex_relay/tests/test_relay.py.
It does not contact the network or execute Codex inference.
"""
from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import sys

TARGET = Path("portfolio_autopilot/codex_relay/tests/test_relay.py")
CODEX = Path("portfolio_autopilot/codex_relay/codex.py")

OLD = """        self.assertEqual(rpc.calls[0][1]['sandbox'],'read-only')
        self.assertEqual(next(p for m,p in rpc.calls if m=='turn/start')['outputSchema'],OUTPUT_SCHEMA)"""
NEW = """        thread_params = rpc.calls[0][1]
        self.assertEqual(thread_params['permissions'], 'relay-locked')
        self.assertNotIn('sandbox', thread_params)
        turn_params = next(p for m,p in rpc.calls if m == 'turn/start')
        self.assertEqual(turn_params['permissions'], 'relay-locked')
        self.assertNotIn('sandboxPolicy', turn_params)
        self.assertEqual(turn_params['outputSchema'], OUTPUT_SCHEMA)"""


def main() -> int:
    if not (TARGET.is_file() and CODEX.is_file() and Path("AGENTS.md").is_file()):
        print("ERROR: Run this from the root of the Proj repository.")
        return 1
    code = CODEX.read_text(encoding="utf-8")
    if code.count('"permissions": "relay-locked"') != 2 or '"sandboxPolicy": {"type": "readOnly", "access"' in code:
        print("ERROR: The patched Codex Relay code does not match the expected permission-profile version; no changes made.")
        return 1

    original_bytes = TARGET.read_bytes()
    original = original_bytes.decode("utf-8")
    newline = "\r\n" if b"\r\n" in original_bytes else "\n"
    source = original.replace("\r\n", "\n")
    if OLD not in source or source.count(OLD) != 1:
        if NEW in source:
            print("Test already updated; no changes necessary.")
            return 0
        print("ERROR: Expected test assertion was not found exactly once; no changes made.")
        return 1

    updated = source.replace(OLD, NEW, 1)
    compile(updated, str(TARGET), "exec")
    backup_dir = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CodexRelay" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / ("test_relay_before_permissions_test_update_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".py")
    with backup.open("xb") as handle:
        handle.write(original_bytes)
    TARGET.write_bytes(updated.replace("\n", newline).encode("utf-8"))
    print("SUCCESS: Updated the Codex Relay permission-profile test expectations.")
    print(f"Changed: {TARGET}")
    print(f"Backup: {backup}")
    print("Next: python -m unittest discover -s portfolio_autopilot/codex_relay/tests -v")
    return 0


if __name__ == "__main__":
    sys.exit(main())
