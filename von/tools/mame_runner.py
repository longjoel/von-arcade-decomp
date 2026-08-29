#!/usr/bin/env python3
"""Run a reproducible MAME session against the local Virtual-On artifacts."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mame", required=True, type=Path, help="MAME executable")
    parser.add_argument("--set", default="vonj", help="MAME set name; choose explicitly after ROM identification")
    parser.add_argument("--rom-dir", type=Path, default=Path(__file__).parents[1] / "artifacts")
    parser.add_argument("--capture-dir", type=Path, default=Path(__file__).parents[1] / "captures")
    parser.add_argument("--record-input", type=Path, help="MAME input recording file")
    parser.add_argument("extra", nargs=argparse.REMAINDER, help="Arguments after -- are passed to MAME")
    args = parser.parse_args()

    if not args.mame.is_file() or not os.access(args.mame, os.X_OK):
        parser.error(f"MAME executable is not runnable: {args.mame}")
    if not args.rom_dir.is_dir():
        parser.error(f"ROM directory does not exist: {args.rom_dir}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.capture_dir / f"{args.set}-{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(args.mame),
        args.set,
        "-rompath", str(args.rom_dir),
        "-cfg_directory", str(output_dir / "cfg"),
        "-nvram_directory", str(output_dir / "nvram"),
        "-input_directory", str(output_dir / "inp"),
        "-snapshot_directory", str(output_dir / "snap"),
    ]
    if args.record_input:
        command += ["-record", str(args.record_input)]
    command += [arg for arg in args.extra if arg != "--"]
    print("Launching:", " ".join(subprocess.list2cmdline([arg]) for arg in command))
    print(f"Capture directory: {output_dir}")
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
