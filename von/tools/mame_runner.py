#!/usr/bin/env python3
"""Run a reproducible MAME session against the local Virtual-On artifacts."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


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
        return f"{label} directory does not exist: {path}"
    if not directory and not path.is_file():
        return f"{label} file does not exist: {path}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mame", required=True, type=Path, help="MAME executable")
    parser.add_argument("--set", default="vonj", help="MAME set name; choose explicitly after ROM identification")
    parser.add_argument("--rom-dir", type=Path, default=Path(__file__).parents[1] / "artifacts")
    parser.add_argument("--capture-dir", type=Path, default=Path(__file__).parents[1] / "captures")
    parser.add_argument("--record-input", type=Path, help="MAME input recording file")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="root that ROM, capture, and input paths must remain within")
    parser.add_argument("extra", nargs=argparse.REMAINDER, help="Arguments after -- are passed to MAME")
    args = parser.parse_args()

    if not args.mame.is_file() or not os.access(args.mame, os.X_OK):
        parser.error(f"MAME executable is not runnable: {args.mame}")
    root = args.root.resolve()
    for label, path, directory, allow_missing in (("ROM", args.rom_dir, True, False),
                                                   ("capture", args.capture_dir, True, True)):
        error = path_error(label, path, root, directory=directory, allow_missing=allow_missing)
        if error:
            parser.error(error)
    if args.record_input:
        error = path_error("record input", args.record_input, root)
        if error:
            parser.error(error)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.capture_dir / f"{args.set}-{stamp}"
    try:
        output_dir.resolve().relative_to(root)
    except (OSError, RuntimeError, ValueError):
        parser.error(f"capture output path escapes root: {output_dir}")
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
