#!/usr/bin/env python3
"""Check generated reconstruction status without overwriting it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_status import collect, markdown


def check(root: Path, expected: Path) -> list[str]:
    if expected.is_symlink():
        return [f"status path must not be a symlink: {expected}"]
    try:
        actual = expected.read_text(encoding="utf-8")
        generated = markdown(collect(root))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        return [f"unable to generate or read status: {error}"]
    if actual != generated:
        return [f"stale generated status: {expected}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--status", type=Path, default=Path("von/generated-status.md"))
    args = parser.parse_args()
    errors = check(args.root.resolve(), args.status)
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Status freshness: {args.status} is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
