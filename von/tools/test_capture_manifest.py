#!/usr/bin/env python3
"""Contract tests for bounded capture sidecar manifests."""

from __future__ import annotations

import copy
import tempfile
from pathlib import Path

from capture_manifest import directory_sha256, entry, validate


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name in ("cfg", "nvram", "state"):
            (root / name).mkdir()
        input_path = root / "rom-manifest.json"
        artifact_path = root / "events.ndjson"
        input_path.write_text('{"rom": "fixture"}\n', encoding="utf-8")
        artifact_path.write_text('{"seq": 1}\n', encoding="utf-8")
        report_path = root / "coverage.json"
        report_path.write_text('{"capture_id": "fixture-v1", "tier": "A", "phase": "stable-attract"}\n', encoding="utf-8")
        manifest = {
            "schema_version": 1, "id": "fixture-v1", "objective": "test-capture",
            "stimulus": {"kind": "input-free-attract", "seconds": 1, "phase": "stable-attract"},
            "configuration": {"set": "fixture", "mame_revision": "abc",
                               "patch_profile": "none", "execution_engine": "interpreter"},
            "command": ["mame", "vonj", "-video", "none"],
            "isolation": {"cfg_directory": "cfg", "nvram_directory": "nvram", "state_directory": "state"},
            "inputs": [entry(input_path, root)], "artifacts": [entry(artifact_path, root)],
            "coverage_report": "coverage.json",
        }
        for field in ("cfg_directory", "nvram_directory", "state_directory"):
            manifest["isolation"][f"{field}_sha256"] = directory_sha256(root / manifest["isolation"][field])
        assert not validate(manifest, root)
        broken = copy.deepcopy(manifest)
        broken["artifacts"][0]["sha256"] = "0" * 64
        assert any("hash mismatch" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"][0]["sha256"] = "invalid"
        assert any("must be a SHA-256" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["command"] = []
        assert any("command" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["stimulus"]["phase"] = "startup"
        assert any("phase" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["coverage_report"] = "coverage.json"
        report_path.write_text('{"capture_id": "other", "tier": "A"}\n', encoding="utf-8")
        assert any("capture_id" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"][0]["path"] = "../outside.log"
        assert any("missing file" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = []
        assert any("at least one artifact" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken.pop("coverage_report")
        assert any("requires coverage_report" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["objective"] = ""
        assert any("objective" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["stimulus"]["seconds"] = -1
        assert any("numeric seconds" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = ["malformed"]
        assert any("must be an object" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["inputs"] = {"path": "rom-manifest.json"}
        assert any("inputs must be an array" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"].append(copy.deepcopy(broken["artifacts"][0]))
        assert any("duplicate file" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["isolation"]["nvram_directory"] = "cfg"
        broken["isolation"]["nvram_directory_sha256"] = broken["isolation"]["cfg_directory_sha256"]
        assert any("directories must be distinct" in error for error in validate(broken, root))
        outside = root.parent / "outside-capture-fixture.txt"
        outside.write_text("outside\n", encoding="utf-8")
        link = root / "linked-artifact.txt"
        link.symlink_to(outside)
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = [{"path": "linked-artifact.txt", "sha256": ""}]
        assert any("missing file" in error for error in validate(broken, root))
        causal = copy.deepcopy(manifest)
        causal["stimulus"]["kind"] = "causal-trace"
        causal.pop("coverage_report")
        assert not validate(causal, root)
    print("PASS: capture sidecar manifest hashes and provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
