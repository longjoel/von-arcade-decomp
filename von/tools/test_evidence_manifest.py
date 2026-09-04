#!/usr/bin/env python3
"""Contract test for the tracked evidence manifest."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from capture_manifest import directory_sha256, entry
from evidence_manifest import validate


def main() -> int:
    root = Path.cwd()
    manifest = json.loads((root / "von/evidence/manifest.json").read_text(encoding="utf-8"))
    ledger = json.loads((root / "von/reconstruction_ledger.json").read_text(encoding="utf-8"))
    assert not validate(manifest, ledger, root)
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["outcome"] = "incomplete"
    assert any("outcome" in error for error in validate(broken, ledger, root))
    runtime = json.loads(json.dumps(manifest))
    runtime["entries"][0]["stimulus"] = {
        "kind": "input-free-attract", "description": "runtime fixture"
    }
    assert any("capture_manifest" in error for error in validate(runtime, ledger, root))
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        for name in ("cfg", "nvram", "state"):
            (temp / name).mkdir()
        summary = temp / "summary.json"
        summary.write_text('{"capture_id":"capture-v1","tier":"A"}\n', encoding="utf-8")
        verifier = temp / "verify.py"
        verifier.write_text("# verifier\n", encoding="utf-8")
        capture = {
            "schema_version": 1, "id": "capture-v1", "objective": "pilot",
            "stimulus": {"kind": "input-free-attract", "seconds": 1},
            "configuration": {"set": "vonj", "mame_revision": "abc", "patch_profile": "none", "execution_engine": "interpreter"},
            "command": ["mame", "vonj"],
            "isolation": {"cfg_directory": "cfg", "nvram_directory": "nvram", "state_directory": "state"},
            "coverage_report": "summary.json", "inputs": [], "artifacts": [entry(summary, temp)],
        }
        for field in ("cfg_directory", "nvram_directory", "state_directory"):
            capture["isolation"][f"{field}_sha256"] = directory_sha256(temp / capture["isolation"][field])
        (temp / "capture.json").write_text(json.dumps(capture), encoding="utf-8")
        runtime = {
            "entries": [{"id": "capture-v1", "canonical": True,
                         "stimulus": {"kind": "input-free-attract", "description": "pilot"},
                         "configuration": capture["configuration"], "artifacts": capture["artifacts"],
                         "capture_manifest": "capture.json", "verifier": "verify.py",
                         "outcome": "pass", "consumers": ["unit"]}],
        }
        assert not validate(runtime, {"images": [{"work_units": [{"id": "unit"}]}]}, temp)
        capture["id"] = "other"
        (temp / "capture.json").write_text(json.dumps(capture), encoding="utf-8")
        assert any("does not match evidence id" in error for error in validate(runtime, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
    print("PASS: canonical evidence manifest contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
