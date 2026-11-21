"""Smoke-test editor plugin registration and a marker scene in a temporary project."""
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
    executable = Path(parser.parse_args().godot).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="editor-check-", dir=ROOT) as scratch:
        project = Path(scratch).resolve()
        if project.parent != ROOT:
            raise RuntimeError("Unexpected temporary directory")
        (project / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="Editor check"\n'
            '[editor_plugins]\nenabled=PackedStringArray("res://addons/transit_coordinator/plugin.cfg")\n',
            encoding="utf-8",
        )
        shutil.copytree(ROOT / "addons", project / "addons")
        plugin = project / "addons/transit_coordinator/editor/plugin.gd"
        source = plugin.read_text(encoding="utf-8-sig")
        original = "add_node_3d_gizmo_plugin(_gizmo)"
        if source.count(original) != 1:
            raise RuntimeError("Editor registration changed; update this smoke test")
        plugin.write_text(source.replace(original, original + '\n\tprint("TRANSIT_EDITOR_GIZMO_REGISTERED")'), encoding="utf-8")
        gizmo = project / "addons/transit_coordinator/editor/stop_gizmo.gd"
        gizmo_source = gizmo.read_text(encoding="utf-8-sig")
        expected = "return node.get_script() == Marker"
        if gizmo_source.count(expected) != 1:
            raise RuntimeError("Marker recognition changed; update this smoke test")
        gizmo_source = gizmo_source.replace(expected, 'if node.get_script() == Marker:\n\t\tprint("TRANSIT_EDITOR_MARKER_RECOGNIZED")\n\t\treturn true\n\treturn false')
        redraw = "gizmo.add_lines(lines,get_material(\"stop\",gizmo))"
        if gizmo_source.count(redraw) != 1:
            raise RuntimeError("Gizmo drawing changed; update this smoke test")
        gizmo.write_text(gizmo_source.replace(redraw, redraw + '\n\tprint("TRANSIT_EDITOR_GIZMO_REDRAWN")'), encoding="utf-8")
        (project / "marker.tscn").write_text(
            '[gd_scene load_steps=2 format=3]\n\n'
            '[ext_resource type="Script" path="res://addons/transit_coordinator/editor/stop_marker.gd" id="1"]\n\n'
            '[node name="Stop" type="Node3D"]\nscript = ExtResource("1")\nstop_id = "hub"\n',
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["APPDATA"] = str(project / "appdata")
        env["LOCALAPPDATA"] = env["APPDATA"]
        result = subprocess.run(
            [str(executable), "--headless", "--editor", "--path", str(project), "res://marker.tscn", "--quit-after", "120"],
            capture_output=True, text=True, env=env, timeout=90,
        )
        output = result.stdout + result.stderr
        print(output.strip())
        unexpected = [line for line in output.splitlines() if "ERROR:" in line and "Failed to read the root certificate store" not in line]
        if result.returncode or "TRANSIT_EDITOR_GIZMO_REGISTERED" not in output or "TRANSIT_EDITOR_MARKER_RECOGNIZED" not in output or "TRANSIT_EDITOR_GIZMO_REDRAWN" not in output or "SCRIPT ERROR" in output or unexpected:
            return 1
        print("Editor plugin registration: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
