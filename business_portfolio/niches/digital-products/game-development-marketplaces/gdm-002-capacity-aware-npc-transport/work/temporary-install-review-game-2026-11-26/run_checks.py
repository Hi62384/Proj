"""Run the temporary game's headless integration checks in isolated user data."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
CASES = {
    "test_transfer.gd": "Independent temporary game transfer: PASS",
    "test_midride_restore.gd": "Independent temporary game midride restore: PASS",
    "test_full_world_restore.gd": "Independent temporary game full world restore: PASS",
    "test_interruption.gd": "Independent temporary game interruption: PASS",
    "test_onboard_cancellation.gd": "Independent temporary game onboard cancellation: PASS",
    "test_navigation_adapter.gd": "Temporary game navigation adapter ride: PASS",
    "test_navigation_recovery.gd": "Temporary game navigation recovery: PASS",
    "test_blocked_crowd_restore.gd": "Temporary game blocked crowd recovery restore: PASS",
    "test_crowd_destroyed_recovery.gd": "Temporary game destroyed passenger recovery: PASS",
}

if len(sys.argv) != 2:
    raise SystemExit("Usage: python run_checks.py <Godot console executable>")
godot = Path(sys.argv[1]).resolve(strict=True)
with tempfile.TemporaryDirectory(prefix="gdm-independent-game-") as scratch:
    env = os.environ.copy()
    env["APPDATA"] = scratch
    env["LOCALAPPDATA"] = scratch
    for script, expected in CASES.items():
        result = subprocess.run([str(godot), "--headless", "--path", str(ROOT), "--script", "res://" + script],
                                env=env, text=True, capture_output=True, timeout=120)
        output = result.stdout + result.stderr
        errors = [line for line in output.splitlines() if "ERROR:" in line and "Failed to read the root certificate store" not in line]
        passed = result.returncode == 0 and expected in output and "SCRIPT ERROR" not in output and not errors
        print(f"{script}: {'PASS' if passed else 'FAIL'}", flush=True)
        if not passed:
            print(output)
            raise SystemExit(1)
print(f"Temporary independent game: {len(CASES)}/{len(CASES)} passed")
