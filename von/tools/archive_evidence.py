#!/usr/bin/env python3
"""Copy a raw capture into the ignored content-addressed evidence archive."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--archive", type=Path, default=Path("von/build/evidence/sha256"))
    parser.add_argument("--quarantine", action="store_true", help="also preserve the original under quarantine")
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
    print(f"sha256:{digest} {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
