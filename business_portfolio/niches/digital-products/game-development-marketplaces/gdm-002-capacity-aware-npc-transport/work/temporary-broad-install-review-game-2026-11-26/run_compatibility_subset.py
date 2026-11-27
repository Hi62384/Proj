"""Run eight bounded broad integration cases with isolated Godot user data."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
CASES = {
    "test_moving_crowd.gd": "Temporary game moving crowd avoidance: PASS",
    "test_four_moving_crowd.gd": "Temporary game four-moving-passenger crowd avoidance: PASS",
    "test_mapped_physical_dispatch.gd": "Temporary game event-mapped physical dispatch: PASS",
    "test_capacity_two_crossing_restore.gd": "Temporary game capacity-two crossing reconstruction: PASS",
    "test_navigation_unreachable.gd": "Disconnected navigation boarding integration: PASS",
    "test_parallel_recovery_restore.gd": "Temporary game parallel recovery reconstruction: PASS",
    "test_footprint_clearance.gd": "Temporary game footprint clearance: PASS",
    "test_endpoint_clearance.gd": "Temporary game endpoint clearance: PASS",
}
if len(sys.argv) != 2:
    raise SystemExit("Usage: python run_compatibility_subset.py <Godot console executable>")
engine = Path(sys.argv[1]).resolve(strict=True)
failed = []
with tempfile.TemporaryDirectory(prefix="gdm-broad-subset-") as scratch:
    env = os.environ.copy()
    env["APPDATA"] = scratch
    env["LOCALAPPDATA"] = scratch
    for script, expected in CASES.items():
        try:
            result = subprocess.run([str(engine), "--headless", "--path", str(ROOT), "--script", "res://" + script],
                                    env=env, text=True, capture_output=True, timeout=90)
            output = result.stdout + result.stderr
            unexpected = [line for line in output.splitlines() if "ERROR:" in line and "Failed to read the root certificate store" not in line]
            passed = result.returncode == 0 and expected in output and "SCRIPT ERROR" not in output and not unexpected
        except subprocess.TimeoutExpired:
            output = "Timed out after 90 seconds."
            passed = False
        print(f"{script}: {'PASS' if passed else 'FAIL'}", flush=True)
        if not passed:
            failed.append(script)
            print(output[-3000:], flush=True)
print(f"Broad integration subset: {len(CASES) - len(failed)}/{len(CASES)} passed")
raise SystemExit(1 if failed else 0)
