#!/usr/bin/env python3
"""Report the authoritative reconstruction, test, and evidence status."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from evidence_manifest import validate as validate_evidence
from reconstruction_ledger import code_coverage, validate as validate_ledger
from run_tests import commands_for


def test_results(root: Path, manifest_bytes: bytes, suite_commands: dict[str, list[list[str]]]) -> dict[str, dict]:
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    results = {}
    for suite_name, commands in suite_commands.items():
        path = root / "von/build/test-results" / f"{suite_name}.json"
        if not path.is_file():
            results[suite_name] = {"state": "not-run"}
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            results[suite_name] = {"state": "invalid"}
            continue
        stale = document.get("manifest_sha256") != digest or document.get("commands") != commands
        state = "stale" if stale else ("pass" if document.get("passed") else "fail")
        results[suite_name] = {
            "state": state,
            "tests": document.get("tests"),
            "completed_at": document.get("completed_at"),
            "failures": document.get("failures", []),
        }
    return results


def collect(root: Path) -> dict:
    ledger = json.loads((root / "von/reconstruction_ledger.json").read_text(encoding="utf-8"))
    worklist = json.loads((root / "von/attract_worklist.json").read_text(encoding="utf-8"))
    evidence = json.loads((root / "von/evidence/manifest.json").read_text(encoding="utf-8"))
    test_manifest_path = root / "von/tests/manifest.json"
    test_manifest_bytes = test_manifest_path.read_bytes()
    test_manifest = json.loads(test_manifest_bytes)
    ledger_errors = validate_ledger(ledger, root)
    evidence_errors = validate_evidence(evidence, ledger, root)
    stages = Counter(unit["stage"] for image in ledger["images"] for unit in image["work_units"])
    test_commands = {name: commands_for(root, test_manifest, name)[0] for name in test_manifest["suites"]}
    test_counts = {name: len(commands) for name, commands in test_commands.items()}
    canonical = [entry for entry in evidence["entries"] if entry.get("canonical")]
    return {
        "objective": ledger.get("objective"),
        "ledger": {
            "valid": not ledger_errors,
            "errors": ledger_errors,
            "work_units": sum(stages.values()),
            "stages": dict(sorted(stages.items())),
            "physical_code_bytes": code_coverage(ledger)["total"],
        },
        "attract": {
            key: worklist[key] for key in (
                "discovered_units", "modeled_units", "integrated_units", "untriaged_units"
            )
        },
        "tests": {
            "manifest_valid": True,
            "configured": test_counts,
            "fast_requires_mame": False,
            "last_results": test_results(root, test_manifest_bytes, test_commands),
        },
        "evidence": {
            "healthy": not evidence_errors,
            "canonical": len(canonical),
            "errors": evidence_errors,
        },
    }


def markdown(status: dict) -> str:
    stages = status["ledger"]["stages"]
    attract = status["attract"]
    tests = status["tests"]["configured"]
    outcomes = status["tests"]["last_results"]
    outcome_text = "; ".join(f"{name}={value['state']}" for name, value in outcomes.items())
    return "\n".join([
        "# Generated Reconstruction Status", "",
        "Generated from `von/reconstruction_ledger.json`, `von/attract_worklist.json`,",
        "`von/tests/manifest.json`, and `von/evidence/manifest.json`.", "",
        f"- Active objective: `{status['objective']}`",
        f"- Ledger: {'valid' if status['ledger']['valid'] else 'invalid'} ({len(status['ledger']['errors'])} errors)",
        f"- Work units: {status['ledger']['work_units']} total; {stages.get('modeled', 0)} modeled; {stages.get('integrated', 0)} integrated; {stages.get('trace-validated', 0)} trace-validated; {stages.get('byte-validated', 0)} byte-validated",
        f"- Physical code union: {status['ledger']['physical_code_bytes']:,} bytes",
        f"- Attract worklist: {attract['discovered_units']} discovered; {attract['modeled_units']} modeled integration queue; {attract['integrated_units']} integrated; {attract['untriaged_units']} untriaged",
        f"- Tests configured: {tests['unit']} unit; {tests['contract']} contract; {tests['trace']} trace; {tests['smoke']} smoke; {tests['attract']} attract",
        f"- Latest test results: {outcome_text}",
        f"- Evidence: {status['evidence']['canonical']} canonical; {'healthy' if status['evidence']['healthy'] else 'invalid'}",
        "",
        "Regenerate with `./scripts/status.sh --write-markdown`.", "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-markdown", action="store_true")
    args = parser.parse_args()
    root = Path.cwd()
    status = collect(root)
    if args.write_markdown:
        (root / "von/generated-status.md").write_text(markdown(status), encoding="utf-8")
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(markdown(status), end="")
    return 0 if status["ledger"]["valid"] and status["evidence"]["healthy"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
