#!/usr/bin/env python3
"""Copy a raw capture into the ignored content-addressed evidence archive."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_metadata(metadata: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if metadata.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for section in ("source", "archive"):
        item = metadata.get(section, {})
        path = Path(item.get("path", ""))
        if not path.is_file():
            errors.append(f"missing {section} file {item.get('path')}")
            continue
        if item.get("bytes") != path.stat().st_size:
            errors.append(f"{section} byte count mismatch")
        if item.get("sha256") != sha256(path):
            errors.append(f"{section} hash mismatch")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--archive", type=Path, default=Path("von/build/evidence/sha256"))
    parser.add_argument("--quarantine", action="store_true", help="also preserve the original under quarantine")
    parser.add_argument("--metadata", type=Path,
                        help="write source/archive hashes and sizes to this JSON file")
    args = parser.parse_args()
    payload = args.capture.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    args.archive.mkdir(parents=True, exist_ok=True)
    target = args.archive / f"{digest}.gz"
    if not target.exists():
        with gzip.GzipFile(filename=str(target), mode="wb", mtime=0) as stream:
            stream.write(payload)
    if args.quarantine:
        quarantine = Path("von/build/evidence/quarantine")
        quarantine.mkdir(parents=True, exist_ok=True)
        preserved = quarantine / args.capture.name
        if not preserved.exists():
            shutil.copy2(args.capture, preserved)
    if args.metadata:
        args.metadata.parent.mkdir(parents=True, exist_ok=True)
        args.metadata.write_text(json.dumps({
            "schema_version": 1,
            "source": {"path": str(args.capture), "bytes": len(payload), "sha256": digest},
            "archive": {"path": str(target), "bytes": target.stat().st_size, "sha256": sha256(target)},
        }, indent=2) + "\n", encoding="utf-8")
    print(f"sha256:{digest} {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
