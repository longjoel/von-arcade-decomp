#!/usr/bin/env python3
"""Build a portable, provenance-first asset catalog from a showcase manifest."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


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
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    entries = []
    for entry in manifest["assets"]:
        path = args.asset_root / entry["path"].lstrip("/")
        if not path.is_file():
            raise SystemExit(f"missing asset: {path}")
        record = {key: entry[key] for key in ("id", "displayName", "category", "status", "sourceTrace",
                                               "evidencePath", "reviewNotes", "rejectionReason", "showcase")
                  if key in entry}
        record["file"] = entry["path"]
        record["geometry"] = gltf_summary(path)
        if entry.get("evidencePath"):
            evidence = args.asset_root / entry["evidencePath"].lstrip("/")
            if not evidence.is_file():
                raise SystemExit(f"missing evidence: {evidence}")
            record["evidence"] = json.loads(evidence.read_text())
        entries.append(record)
    catalog = {"version": 1, "assets": entries,
               "counts": {status: sum(entry["status"] == status for entry in entries)
                          for status in ("verified", "candidate", "rejected")}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, indent=2) + "\n")
    print(f"cataloged {len(entries)} assets: {catalog['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
