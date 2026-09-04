#!/usr/bin/env python3
"""Check that a tracked worklist matches its generator without overwriting it."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "von/tools/build_attract_worklist.py"


def normalized(document: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(document))
    result.pop("coverage_source", None)
    return result


def check(coverage: Path, ledger: Path, expected: Path, root: Path,
          expected_markdown: Path | None = None) -> list[str]:
    try:
        coverage_document = json.loads(coverage.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"unable to read coverage JSON: {error}"]
    if not isinstance(coverage_document, dict):
        return [f"invalid coverage JSON object: {coverage}"]
    if coverage_document.get("tier") != "A" or coverage_document.get("edge_semantics") != "possible_static_edges":
        return [f"stale or invalid Tier A coverage: {coverage}"]
    with tempfile.TemporaryDirectory() as directory:
        generated = Path(directory)
        result = subprocess.run(
            [sys.executable, str(GENERATOR), "--coverage", str(coverage), "--ledger", str(ledger),
             "--json", str(generated / "worklist.json"), "--markdown", str(generated / "worklist.md")],
            cwd=root, capture_output=True, text=True, check=False,
        )
        if result.returncode:
            return [f"worklist generator failed: {result.stderr.strip()}"]
        try:
            actual = json.loads(expected.read_text(encoding="utf-8"))
            generated_json = json.loads((generated / "worklist.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            return [f"unable to read worklist JSON: {error}"]
        if not isinstance(actual, dict) or not isinstance(generated_json, dict):
            return [f"invalid worklist JSON object: {expected}"]
        if normalized(actual) != normalized(generated_json):
            return [f"stale worklist JSON: {expected}"]
        if expected_markdown is not None:
            generated_markdown = (generated / "worklist.md").read_text(encoding="utf-8")
            if expected_markdown.read_text(encoding="utf-8") != generated_markdown:
                return [f"stale worklist Markdown: {expected_markdown}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--worklist", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    errors = check(args.coverage, args.ledger, args.worklist, args.root, args.markdown)
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Worklist freshness: {args.worklist} is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
