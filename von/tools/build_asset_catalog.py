#!/usr/bin/env python3
"""Build a portable, provenance-first asset catalog from a showcase manifest."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


STATUSES = ("legacy-unreviewed", "candidate", "observed", "validated",
            "rejected", "reference-capture")


def path_error(label: str, path: Path, root: Path, *, directory: bool = False,
               allow_missing: bool = False) -> str | None:
    if path.is_symlink():
        return f"{label} path must not be a symlink: {path}"
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return f"{label} path escapes root: {path}"
    if allow_missing and not path.exists():
        return None
    if directory and not path.is_dir():
        return f"missing {label} directory: {path}"
    if not directory and not path.is_file():
        return f"missing {label}: {path}"
    return None


def asset_path(asset_root: Path, path_text: object, label: str) -> Path:
    if not isinstance(path_text, str) or not path_text:
        raise ValueError(f"{label} path must be a non-empty string")
    candidate = asset_root / path_text.lstrip("/")
    if candidate.is_symlink():
        raise ValueError(f"{label} path must not be a symlink: {candidate}")
    try:
        candidate.resolve().relative_to(asset_root.resolve())
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(f"{label} path escapes asset root: {path_text}") from error
    return candidate


def gltf_summary(path: Path) -> dict[str, int]:
    document = json.loads(path.read_text())
    for accessor in document.get("accessors", []):
        for key in ("min", "max"):
            if key in accessor and not all(math.isfinite(float(value)) for value in accessor[key]):
                raise ValueError(f"{path}: non-finite {key} accessor")
    return {"nodes": len(document.get("nodes", [])), "meshes": len(document.get("meshes", [])),
            "materials": len(document.get("materials", [])), "images": len(document.get("images", []))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="root that manifest, assets, evidence, and output must remain within")
    args = parser.parse_args()
    root = args.root.resolve()
    for label, path, directory, allow_missing in (
            ("manifest", args.manifest, False, False),
            ("asset root", args.asset_root, True, False),
            ("output", args.output, False, True)):
        error = path_error(label, path, root, directory=directory, allow_missing=allow_missing)
        if error:
            print(f"Asset catalog: {error}")
            return 1
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Asset catalog: unable to read manifest: {error}")
        return 1
    if not isinstance(manifest, dict) or not isinstance(manifest.get("assets"), list):
        print("Asset catalog: manifest assets must be an array")
        return 1
    entries = []
    for entry in manifest["assets"]:
        if not isinstance(entry, dict):
            print("Asset catalog: asset entry must be an object")
            return 1
        try:
            path = asset_path(args.asset_root, entry.get("path"), "asset")
        except ValueError as error:
            print(f"Asset catalog: {error}")
            return 1
        if not path.is_file():
            print(f"Asset catalog: missing asset: {path}")
            return 1
        record = {key: entry[key] for key in ("id", "displayName", "category", "status", "sourceTrace",
                                               "evidencePath", "reviewNotes", "rejectionReason", "showcase")
                  if key in entry}
        record["file"] = entry["path"]
        record["geometry"] = gltf_summary(path)
        if entry.get("evidencePath"):
            try:
                evidence = asset_path(args.asset_root, entry["evidencePath"], "evidence")
            except ValueError as error:
                print(f"Asset catalog: {error}")
                return 1
            if not evidence.is_file():
                print(f"Asset catalog: missing evidence: {evidence}")
                return 1
            record["evidence"] = json.loads(evidence.read_text(encoding="utf-8"))
        entries.append(record)
    catalog = {"version": 1, "assets": entries,
               "counts": {status: sum(entry["status"] == status for entry in entries)
                          for status in STATUSES}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2) + "\n")
    print(f"cataloged {len(entries)} assets: {catalog['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
