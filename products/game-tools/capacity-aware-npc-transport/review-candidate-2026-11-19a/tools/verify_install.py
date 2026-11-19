"""Smoke-test copy, removal, and reinstallation in an isolated local Godot project."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("godot", help="Path to the Godot console executable")
    args = parser.parse_args()
    executable = Path(args.godot).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="install-check-", dir=ROOT) as scratch:
        project = Path(scratch).resolve()
        if project.parent != ROOT:
            raise RuntimeError("Unexpected temporary directory")
        (project / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="Installation check"\n',
            encoding="utf-8",
        )
        shutil.copy2(ROOT / "tests" / "install_probe.gd", project / "install_probe.gd")
        env = os.environ.copy()
        env["APPDATA"] = str(project / "appdata")
        for label in ("install", "reinstall"):
            shutil.copytree(ROOT / "addons", project / "addons")
            result = subprocess.run(
                [str(executable), "--headless", "--path", str(project), "--script", "res://install_probe.gd"],
                capture_output=True, text=True, env=env, timeout=60,
            )
            output = result.stdout + result.stderr
            print(f"{label}: {output.strip()}")
            if result.returncode or "Standalone copied add-on: PASS" not in output or "SCRIPT ERROR" in output or "Parse Error" in output:
                return 1
            unexpected = [line for line in output.splitlines() if "ERROR:" in line and "Failed to read the root certificate store" not in line]
            if unexpected:
                return 1
            # Only delete the copy created inside this temporary project.
            target = (project / "addons").resolve()
            if target.parent != project or target.name != "addons":
                raise RuntimeError("Unexpected add-on path")
            shutil.rmtree(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
