#!/usr/bin/env python3
"""Contract tests for evidence asset pack validation."""

from __future__ import annotations

import copy
import hashlib
import tempfile
from pathlib import Path

from validate_asset_pack import validate


def main() -> int:
    assert any("asset pack must be an object" in error for error in validate([], {}, Path.cwd()))
    assert any("evidence manifest must be an object" in error for error in validate({}, [], Path.cwd()))
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        payload = root / "fighter.glb"
        payload.write_bytes(b"fixture-payload")
        pack = {
            "schema_version": 1, "kind": "von-evidence-asset-pack", "id": "pack-v1",
            "basis": {"romset_hash": "a" * 64, "map_revision": "map", "capture_id": "capture-v1", "tool_revision": "tool"},
            "assets": [{"id": "fighter", "media_type": "model", "status": "validated",
                        "payload": "fighter.glb", "sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
                        "claims": {"geometry": "validated", "identity": "candidate"},
                        "evidence_ids": ["capture-v1"], "verifiers": ["verify-fighter"],
                        "verifier_results": {"verify-fighter": "pass"}}],
        }
        evidence = {"entries": [{"id": "capture-v1", "canonical": True, "outcome": "pass"}]}
        assert not validate(pack, evidence, root)
        broken = copy.deepcopy(pack)
        broken["basis"] = []
        assert any("basis must be an object" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["basis"]["tool_revision"] = ["tool"]
        assert any("missing basis.tool_revision" in error for error in validate(broken, evidence, root))
        broken_evidence = {"entries": ["malformed"]}
        assert any("unknown canonical basis" in error for error in validate(pack, broken_evidence, root))
        rom_manifest = root / "rom-manifest.json"
        rom_manifest.write_text('{"rom":"fixture"}\n', encoding="utf-8")
        pack["basis"]["romset_hash"] = hashlib.sha256(rom_manifest.read_bytes()).hexdigest()
        assert not validate(pack, evidence, root, rom_manifest)
        assert not validate(pack, evidence, root, rom_manifest, "tool", "map")
        assert any("tool_revision" in error for error in
                   validate(pack, evidence, root, rom_manifest, "stale-tool", "map"))
        assert any("map_revision" in error for error in
                   validate(pack, evidence, root, rom_manifest, "tool", "stale-map"))
        broken = copy.deepcopy(pack)
        broken["basis"]["romset_hash"] = "0" * 64
        assert any("romset_hash" in error for error in validate(broken, evidence, root, rom_manifest))
        broken["basis"]["romset_hash"] = "rom"
        assert any("must be a SHA-256" in error for error in validate(broken, evidence, root))
        pack["basis"]["romset_hash"] = "a" * 64
        broken = copy.deepcopy(pack)
        broken["assets"][0]["status"] = "verified"
        assert any("invalid status" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["assets"][0]["media_type"] = "unknown-media"
        assert any("unsupported media_type" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["assets"][0]["claims"]["identity"] = True
        assert any("claim/status vocabulary" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["assets"][0]["claims"]["unsupported_claim"] = "candidate"
        assert any("claim/status vocabulary" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["assets"][0]["evidence_ids"] = ["missing"]
        assert any("unknown canonical evidence" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["assets"][0]["evidence_ids"] = [{}]
        assert any("non-empty strings" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["basis"]["capture_id"] = "missing"
        assert any("basis capture id" in error for error in validate(broken, evidence, root))
        failed_evidence = {"entries": [{"id": "capture-v1", "canonical": True, "outcome": "fail"}]}
        assert any("evidence outcome must be pass" in error for error in validate(pack, failed_evidence, root))
        outside = root.parent / "outside-asset-fixture.glb"
        outside.write_bytes(b"outside-payload")
        (root / "linked.glb").symlink_to(outside)
        broken = copy.deepcopy(pack)
        broken["assets"][0]["payload"] = "linked.glb"
        assert any("missing payload" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        del broken["assets"][0]["verifier_results"]
        assert any("passing verifier_results" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["assets"][0]["payload"] = "../outside.glb"
        assert any("missing payload" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["assets"][0]["verifier_results"]["stale-verifier"] = "pass"
        assert any("passing verifier_results" in error for error in validate(broken, evidence, root))
    print("PASS: evidence asset pack validates claims, hashes, and evidence IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
