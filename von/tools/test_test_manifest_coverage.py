#!/usr/bin/env python3
"""Ensure every Python test belongs to exactly one manifest tier."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from run_tests import commands_for


def main() -> int:
    root = Path.cwd()
    manifest = json.loads((root / "von/tests/manifest.json").read_text(encoding="utf-8"))
    assigned: Counter[str] = Counter()
    for suite_name, suite in manifest["suites"].items():
        commands, _ = commands_for(root, manifest, suite_name)
        for command in commands:
            if len(command) >= 2 and command[1].startswith("von/tools/test_") and command[1].endswith(".py"):
                assigned[command[1]] += 1
        for verifier in suite.get("fixture_verifiers", []):
            assigned[verifier] += 1

    discovered = {str(path.relative_to(root)) for path in (root / "von/tools").glob("test_*.py")}
    missing = sorted(discovered - assigned.keys())
    stale = sorted(assigned.keys() - discovered)
    duplicate = sorted(path for path, count in assigned.items() if count != 1)
    if missing or stale or duplicate:
        raise SystemExit(
            f"test manifest mismatch: missing={missing}, stale={stale}, duplicate={duplicate}"
        )
    print(f"PASS: all {len(discovered)} Python tests belong to exactly one tier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
