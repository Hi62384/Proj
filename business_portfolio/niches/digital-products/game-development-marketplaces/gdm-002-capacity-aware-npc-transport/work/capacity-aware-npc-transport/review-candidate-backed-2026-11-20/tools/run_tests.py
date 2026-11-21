"""Run Godot contract/integration scripts and reject hidden script errors."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("godot", help="Godot console executable")
    parser.add_argument("--test", action="append", default=[], help="Exact test filename; repeat to select tests")
    parser.add_argument("--timeout", type=int, default=180, help="Maximum seconds per test")
    args = parser.parse_args()
    executable = Path(args.godot).resolve(strict=True)
    if args.timeout < 1:
        parser.error("timeout must be positive")
    test_dir = ROOT / "tests"
    available = {p.name: p for p in test_dir.glob("test_*.gd") if p.is_file()}
    selected = sorted(args.test if args.test else available)
    if not selected or any(name not in available for name in selected):
        parser.error("select one or more existing test_*.gd filenames")
    version = subprocess.run([str(executable), "--version"], capture_output=True, text=True, timeout=30)
    if version.returncode:
        print(version.stdout + version.stderr, file=sys.stderr)
        return 1
    print("Godot:", version.stdout.strip(), flush=True)
    failed = []
    warnings = 0
    with tempfile.TemporaryDirectory(prefix="test-user-", dir=ROOT) as scratch:
        env = os.environ.copy()
        env["APPDATA"] = scratch
        env["LOCALAPPDATA"] = scratch
        for name in selected:
            try:
                result = subprocess.run(
                    [str(executable), "--headless", "--path", str(ROOT), "--script", f"res://tests/{name}"],
                    capture_output=True, text=True, env=env, timeout=args.timeout,
                )
                output = result.stdout + result.stderr
                warnings += output.count("Failed to read the root certificate store")
                fatal = any(term in output for term in ("SCRIPT ERROR", "Parse Error", "FAIL"))
                fatal |= any("ERROR:" in line and "Failed to read the root certificate store" not in line for line in output.splitlines())
                passed = result.returncode == 0 and "PASS" in output and not fatal
            except subprocess.TimeoutExpired:
                output = "Test exceeded the per-test timeout."
                passed = False
            print(f"{name}: {'PASS' if passed else 'FAIL'}", flush=True)
            if not passed:
                failed.append(name)
                print(output[-8000:], flush=True)
    print(f"Tests: {len(selected) - len(failed)}/{len(selected)} passed; certificate-store warnings: {warnings}", flush=True)
    if failed:
        print("Failed:", ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
