#!/usr/bin/env python3
"""Validate test-result health states and manifest staleness detection."""

import hashlib
import json
import tempfile
from pathlib import Path

from project_status import test_results


def main() -> int:
    manifest = b'{"schema_version":1}'
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "von/build/test-results"
        output.mkdir(parents=True)
        (output / "unit.json").write_text(json.dumps({
            "manifest_sha256": hashlib.sha256(manifest).hexdigest(),
            "passed": True,
            "tests": 3,
            "commands": [["python3", "unit.py"]],
            "completed_at": "2026-01-01T00:00:00+00:00",
            "failures": [],
        }), encoding="utf-8")
        commands = {"unit": [["python3", "unit.py"]], "contract": []}
        states = test_results(root, manifest, commands)
        assert states["unit"]["state"] == "pass"
        assert states["contract"]["state"] == "not-run"
        assert test_results(root, b"changed", {"unit": commands["unit"]})["unit"]["state"] == "stale"
        assert test_results(root, manifest, {"unit": [["python3", "changed.py"]]})["unit"]["state"] == "stale"
    print("PASS: test health reports pass, not-run, and stale states")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
