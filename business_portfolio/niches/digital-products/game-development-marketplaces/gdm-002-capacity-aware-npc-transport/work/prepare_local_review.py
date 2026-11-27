"""Build a local-only product review ZIP from its exact manifest; never publish it."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

WORK = Path(__file__).resolve().parent
SOURCE = WORK / "capacity-aware-npc-transport" / "install-review-performance-notes-2026-11-26"
DESTINATION = WORK / "local-review-artifacts" / "GDM-002-LOCAL-REVIEW-2026-11-26.zip"

def main() -> int:
    if DESTINATION.exists():
        raise SystemExit("Review artifact exists; refusing to overwrite")
    manifest_path = SOURCE / "MANIFEST.json"
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest.decode("utf-8"))
    if manifest.get("status") != "unpublished_review_only" or not isinstance(manifest.get("files"), list):
        raise SystemExit("Invalid local-review manifest")
    payload = {}
    for item in manifest["files"]:
        name = item.get("path")
        if not isinstance(name, str) or not name or "\\" in name or ":" in name:
            raise SystemExit("Invalid manifest path")
        pure = PurePosixPath(name)
        if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts) or name != pure.as_posix() or name in payload or name == "MANIFEST.json":
            raise SystemExit("Unsafe or duplicate manifest path")
        path = SOURCE.joinpath(*pure.parts)
        if any(part.is_symlink() for part in [path, *path.parents] if part != SOURCE.parent) or not path.is_file():
            raise SystemExit("Missing file or link in review source: " + name)
        data = path.read_bytes()
        if len(data) != item.get("bytes") or hashlib.sha256(data).hexdigest() != item.get("sha256"):
            raise SystemExit("Review source differs from manifest: " + name)
        payload[name] = data
    actual = {q.relative_to(SOURCE).as_posix() for q in SOURCE.rglob("*") if q.is_file()}
    if actual != set(payload) | {"MANIFEST.json"}:
        raise SystemExit("Review directory has missing or unexpected files")
    if "LOCAL_REVIEW_ONLY.txt" not in payload:
        raise SystemExit("Local-only notice missing")
    payload["MANIFEST.json"] = raw_manifest
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    try:
        with DESTINATION.open("xb") as output:
            with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for name in sorted(payload):
                    entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    entry.external_attr = 0o100644 << 16
                    archive.writestr(entry, payload[name])
    except FileExistsError:
        raise SystemExit("Review artifact appeared; refusing to overwrite")
    with zipfile.ZipFile(DESTINATION) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(payload):
            raise SystemExit("Artifact verification failed")
        if any(archive.read(name) != data for name, data in payload.items()):
            raise SystemExit("Artifact content differs from source")
    print("Local-only artifact:", DESTINATION)
    print("Files:", len(payload), "SHA-256:", hashlib.sha256(DESTINATION.read_bytes()).hexdigest())
    return 0

if __name__ == "__main__":
    sys.exit(main())
