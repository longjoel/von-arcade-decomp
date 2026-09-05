#!/usr/bin/env python3
"""Copy a raw capture into the ignored content-addressed evidence archive."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any


def has_symlink_component(path: Path) -> bool:
    """Return whether *path* or any of its lexical parents is a symlink."""
    current = path.absolute()
    while True:
        if current.is_symlink():
            return True
        parent = current.parent
        if parent == current:
            return False
        current = parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_metadata(metadata: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(metadata, dict):
        return ["metadata must be an object"]
    if metadata.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for section in ("source", "archive"):
        item = metadata.get(section, {})
        if not isinstance(item, dict):
            errors.append(f"{section} metadata must be an object")
            continue
        path_text = item.get("path", "")
        if not isinstance(path_text, str) or not path_text:
            errors.append(f"missing {section} file {path_text}")
            continue
        path = Path(path_text)
        if has_symlink_component(path):
            errors.append(f"{section} path must not contain symlink components")
            continue
        if not path.is_file():
            errors.append(f"missing {section} file {item.get('path')}")
            continue
        if item.get("bytes") != path.stat().st_size:
            errors.append(f"{section} byte count mismatch")
        if item.get("sha256") != sha256(path):
            errors.append(f"{section} hash mismatch")
    source_item = metadata.get("source", {})
    archive_item = metadata.get("archive", {})
    source = Path(source_item.get("path", "")) if isinstance(source_item, dict) else Path()
    archive = Path(archive_item.get("path", "")) if isinstance(archive_item, dict) else Path()
    source_digest = source_item.get("sha256") if isinstance(source_item, dict) else None
    if archive.is_file() and isinstance(source_digest, str):
        if archive.suffix != ".gz" or archive.name != f"{source_digest}.gz":
            errors.append("archive filename must be the source SHA-256 with .gz suffix")
    if source.is_file() and archive.is_file():
        try:
            with gzip.open(archive, "rb") as stream:
                if stream.read() != source.read_bytes():
                    errors.append("archive decompressed payload mismatch")
        except (OSError, EOFError):
            errors.append("archive is not a readable gzip payload")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--archive", type=Path, default=Path("von/build/evidence/sha256"))
    parser.add_argument("--quarantine", action="store_true", help="also preserve the original under quarantine")
    parser.add_argument("--metadata", type=Path,
                        help="write source/archive hashes and sizes to this JSON file")
    args = parser.parse_args()
    if has_symlink_component(args.capture):
        print("Evidence archive: capture source path must not contain symlink components", file=sys.stderr)
        return 1
    if not args.capture.is_file():
        print(f"Evidence archive: missing capture source: {args.capture}", file=sys.stderr)
        return 1
    if has_symlink_component(args.archive):
        print("Evidence archive: archive directory path must not contain symlink components", file=sys.stderr)
        return 1
    if args.metadata and has_symlink_component(args.metadata):
        print("Evidence archive: metadata path must not contain symlink components", file=sys.stderr)
        return 1
    quarantine = Path("von/build/evidence/quarantine")
    if args.quarantine and has_symlink_component(quarantine):
        print("Evidence archive: quarantine directory path must not contain symlink components", file=sys.stderr)
        return 1
    try:
        payload = args.capture.read_bytes()
    except OSError as error:
        print(f"Evidence archive: unable to read capture source: {error}", file=sys.stderr)
        return 1
    digest = hashlib.sha256(payload).hexdigest()
    args.archive.mkdir(parents=True, exist_ok=True)
    target = args.archive / f"{digest}.gz"
    if has_symlink_component(target):
        print("Evidence archive: digest target path must not contain symlink components", file=sys.stderr)
        return 1
    if target.exists():
        try:
            with gzip.open(target, "rb") as stream:
                existing_payload = stream.read()
        except (OSError, EOFError) as error:
            print(f"Evidence archive: existing archive is unreadable: {error}", file=sys.stderr)
            return 1
        if existing_payload != payload:
            print("Evidence archive: existing digest target payload mismatch", file=sys.stderr)
            return 1
    else:
        with gzip.GzipFile(filename=str(target), mode="wb", mtime=0) as stream:
            stream.write(payload)
    if args.quarantine:
        quarantine.mkdir(parents=True, exist_ok=True)
        preserved = quarantine / args.capture.name
        if has_symlink_component(preserved):
            print("Evidence archive: quarantine target path must not contain symlink components", file=sys.stderr)
            return 1
        if preserved.exists():
            try:
                if preserved.read_bytes() != payload:
                    print("Evidence archive: quarantine target payload mismatch", file=sys.stderr)
                    return 1
            except OSError as error:
                print(f"Evidence archive: quarantine target is unreadable: {error}", file=sys.stderr)
                return 1
        else:
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
