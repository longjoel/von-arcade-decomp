#!/usr/bin/env python3
"""Contract tests for evidence asset pack validation."""

from __future__ import annotations

import copy
import hashlib
import tempfile
from pathlib import Path

from validate_asset_pack import validate


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        payload = root / "fighter.glb"
        payload.write_bytes(b"fixture-payload")
        pack = {
            "schema_version": 1, "kind": "von-evidence-asset-pack", "id": "pack-v1",
            "basis": {"romset_hash": "rom", "map_revision": "map", "capture_id": "capture-v1", "tool_revision": "tool"},
            "assets": [{"id": "fighter", "media_type": "model", "status": "validated",
                        "payload": "fighter.glb", "sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
                        "claims": {"geometry": "validated", "identity": "candidate"},
                        "evidence_ids": ["capture-v1"], "verifiers": ["verify-fighter"],
                        "verifier_results": {"verify-fighter": "pass"}}],
        }
        evidence = {"entries": [{"id": "capture-v1", "canonical": True}]}
        assert not validate(pack, evidence, root)
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
        pack["basis"]["romset_hash"] = "rom"
        broken = copy.deepcopy(pack)
        broken["assets"][0]["status"] = "verified"
        assert any("invalid status" in error for error in validate(broken, evidence, root))
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
        broken["basis"]["capture_id"] = "missing"
        assert any("basis capture id" in error for error in validate(broken, evidence, root))
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
