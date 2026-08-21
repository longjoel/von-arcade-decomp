#!/usr/bin/env python3
"""Verify locally supplied ROMs against the checked-in metadata manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).parents[1] / "rom_manifest.json")
    parser.add_argument("--rom-dir", type=Path, default=Path(__file__).parents[1] / "artifacts")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected = {item["name"]: item for item in manifest["artifacts"]}
    actual = {path.name: path for path in args.rom_dir.iterdir()} if args.rom_dir.exists() else {}
    failures = 0

    for name, item in expected.items():
        path = actual.get(name)
        if path is None:
            print(f"MISSING {name}")
            failures += 1
            continue
        actual_size = path.stat().st_size
        actual_hash = sha256(path)
        size_ok = actual_size == item["size"]
        hash_ok = actual_hash == item["sha256"]
        state = "OK" if size_ok and hash_ok else "MISMATCH"
        print(f"{state:9} {name:20} size={actual_size:8} sha256={actual_hash}")
        if not size_ok or not hash_ok:
            failures += 1

    unexpected = sorted(set(actual) - set(expected))
    for name in unexpected:
        print(f"UNTRACKED {name}")

    if failures:
        print(f"ROM audit failed: {failures} expected artifact(s) missing or changed", file=sys.stderr)
        return 1
    print(f"ROM audit passed: {len(expected)} artifacts verified; set status={manifest['set_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

