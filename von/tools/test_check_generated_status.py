#!/usr/bin/env python3
"""Contract tests for the non-destructive generated status checker."""

from __future__ import annotations

import tempfile
from pathlib import Path

from check_generated_status import check
from project_status import collect, markdown


def main() -> int:
    root = Path.cwd()
    status = root / "von/generated-status.md"
    with tempfile.TemporaryDirectory() as directory:
        current = Path(directory) / "status.md"
        current.write_text(markdown(collect(root)), encoding="utf-8")
        assert not check(root, current)
        stale = Path(directory) / "stale.md"
        stale.write_text(current.read_text(encoding="utf-8") + "\n# stale\n", encoding="utf-8")
        errors = check(root, stale)
        assert errors == [f"stale generated status: {stale}"]
        linked = Path(directory) / "linked-status.md"
        linked.symlink_to(current)
        assert check(root, linked) == [f"status path must not be a symlink: {linked}"]
    print("PASS: generated status freshness is checked without mutation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
