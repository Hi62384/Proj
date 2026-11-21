"""Run reproducible local Godot compatibility checks; no downloads or publication."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SMOKE = [
    "test_core.gd", "test_journeys.gd", "test_disruption.gd",
    "test_continuity_audit.gd", "test_onboard_cancel.gd",
    "test_controller_bridge.gd", "test_controller_bridge_lifecycle.gd",
    "test_game_owned_controller.gd", "test_game_owned_airborne.gd", "test_game_owned_restore.gd", "test_game_owned_midride_restore.gd", "test_debug_overlay.gd", "test_demo.gd", "test_demo_hud.gd",
]


def file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_fingerprint() -> str:
    digest = hashlib.sha256()
    files = [ROOT / "project.godot"]
    for name in ("addons", "demo", "examples", "tests", "tools"):
        folder = ROOT / name
        if folder.exists():
            files.extend(p for p in folder.rglob("*") if p.is_file() and ".godot" not in p.parts and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".uid"))
    for path in sorted(files, key=lambda p: p.relative_to(ROOT).as_posix()):
        name = path.relative_to(ROOT).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(name).to_bytes(8, "big"))
        digest.update(name)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--godot", action="append", required=True, help="Console executable; repeat for each version")
    parser.add_argument("--output", required=True, help="New simple report name (without .json)")
    parser.add_argument("--full", action="store_true", help="Run all tests instead of the documented smoke selection")
    args = parser.parse_args()
    if not args.output or not all(c.isascii() and (c.isalnum() or c in "-_") for c in args.output):
        parser.error("output must be a simple ASCII report name")
    directory = ROOT / "compatibility-results"
    directory.mkdir(exist_ok=True)
    output = directory / f"{args.output}.json"
    if output.exists():
        parser.error("report already exists; choose a new name")
    report = {"created_utc": datetime.now(timezone.utc).isoformat(), "mode": "full" if args.full else "smoke", "source_sha256": source_fingerprint(), "platform": platform.platform(), "machine": platform.machine(), "results": []}
    all_passed = True
    for input_path in args.godot:
        executable = Path(input_path).resolve(strict=True)
        version = subprocess.run([str(executable), "--version"], capture_output=True, text=True, timeout=30)
        item = {"executable_name": executable.name, "executable_sha256": file_sha256(executable), "version": version.stdout.strip(), "checks": []}
        if executable.name.lower().endswith("_console.exe"):
            runtime = executable.with_name(executable.name[:-len("_console.exe")] + ".exe")
            if not runtime.is_file():
                item["checks"].append({"name": "engine_binary", "passed": False, "output": "Companion engine executable is missing."})
                all_passed = False
                report["results"].append(item)
                continue
            item["engine_binary_name"] = runtime.name
            item["engine_binary_sha256"] = file_sha256(runtime)
        if version.returncode:
            item["checks"].append({"name": "version", "passed": False, "output": (version.stdout + version.stderr)[-4000:]})
            all_passed = False
            report["results"].append(item)
            continue
        print("Checking", item["version"], flush=True)
        test_cmd = [sys.executable, str(ROOT / "tools/run_tests.py"), str(executable)]
        if not args.full:
            for test in SMOKE:
                test_cmd.extend(["--test", test])
        checks = [("tests", test_cmd, 10800),
                  ("install_reinstall", [sys.executable, str(ROOT / "tools/verify_install.py"), str(executable)], 180),
                  ("editor_marker", [sys.executable, str(ROOT / "tools/verify_editor.py"), str(executable)], 180)]
        for name, command, timeout in checks:
            print("  Running", name, flush=True)
            try:
                run = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
                passed = run.returncode == 0
                text = run.stdout + run.stderr
            except subprocess.TimeoutExpired:
                passed = False
                text = "Check timed out."
            item["checks"].append({"name": name, "passed": passed, "output": text[-16000:]})
            print(" ", name, "PASS" if passed else "FAIL", flush=True)
            all_passed &= passed
        report["results"].append(item)
    report["source_sha256_after"] = source_fingerprint()
    report["source_unchanged"] = report["source_sha256"] == report["source_sha256_after"]
    if not report["source_unchanged"]:
        print("Source changed while checks were running; results are not a single-source matrix.", file=sys.stderr)
        all_passed = False
    with output.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print("Wrote", output, flush=True)
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
