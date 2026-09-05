#!/usr/bin/env python3
"""Contract tests for evidence asset pack validation."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from validate_asset_pack import validate


TOOL = Path(__file__).resolve().parent / "validate_asset_pack.py"


def main() -> int:
    assert any("asset pack must be an object" in error for error in validate([], {}, Path.cwd()))
    assert any("evidence manifest must be an object" in error for error in validate({}, [], Path.cwd()))
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        payload = root / "fighter.glb"
        payload.write_bytes(b"fixture-payload")
        verifier = root / "verify-fighter.py"
        verifier.write_text("# verifier\n", encoding="utf-8")
        pack = {
            "schema_version": 1, "kind": "von-evidence-asset-pack", "id": "pack-v1",
            "basis": {"romset_hash": "a" * 64, "map_revision": "map", "capture_id": "capture-v1", "tool_revision": "tool"},
            "assets": [{"id": "fighter", "media_type": "model", "status": "validated",
                        "payload": "fighter.glb", "sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
                        "claims": {"geometry": "validated", "source_ranges": "validated",
                                   "transform_association": "validated", "identity": "candidate"},
                        "evidence_ids": ["capture-v1"], "verifiers": ["verify-fighter"],
                        "verifier_results": {"verify-fighter": "pass"}}],
        }
        evidence = {"entries": [{"id": "capture-v1", "canonical": True, "outcome": "pass",
                                  "verifier": "verify-fighter.py",
                                  "verifier_sha256": hashlib.sha256(verifier.read_bytes()).hexdigest()}]}
        assert not validate(pack, evidence, root)
        broken = copy.deepcopy(pack)
        broken["basis"] = []
        assert any("basis must be an object" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["id"] = ["pack-v1"]
        assert any("missing pack id" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["basis"]["tool_revision"] = ["tool"]
        assert any("missing basis.tool_revision" in error for error in validate(broken, evidence, root))
        broken_evidence = {"entries": ["malformed"]}
        assert any("unknown canonical basis" in error for error in validate(pack, broken_evidence, root))
        malformed_entry_errors = validate(pack, broken_evidence, root)
        assert any("entry must be an object" in error for error in malformed_entry_errors)
        duplicate_evidence = {"entries": [
            {"id": "capture-v1", "canonical": True, "outcome": "pass"},
            {"id": "capture-v1", "canonical": True, "outcome": "pass"},
        ]}
        assert any("duplicate evidence id" in error for error in validate(
            pack, duplicate_evidence, root))
        malformed_canonical = copy.deepcopy(evidence)
        malformed_canonical["entries"][0]["canonical"] = "true"
        assert any("canonical must be boolean" in error for error in validate(
            pack, malformed_canonical, root))
        missing_verifier_hash = copy.deepcopy(evidence)
        del missing_verifier_hash["entries"][0]["verifier_sha256"]
        assert any("requires verifier_sha256" in error for error in validate(
            pack, missing_verifier_hash, root))
        stale_verifier_hash = copy.deepcopy(evidence)
        stale_verifier_hash["entries"][0]["verifier_sha256"] = "0" * 64
        assert any("verifier hash mismatch" in error for error in validate(
            pack, stale_verifier_hash, root))
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
        linked_rom_manifest = root / "linked-rom-manifest.json"
        linked_rom_manifest.symlink_to(rom_manifest)
        assert any("missing ROM manifest" in error for error in validate(
            pack, evidence, root, linked_rom_manifest))
        outside_rom_manifest = root.parent / "outside-rom-manifest.json"
        outside_rom_manifest.write_text('{"rom":"outside"}\n', encoding="utf-8")
        assert any("escapes pack root" in error for error in validate(
            pack, evidence, root, outside_rom_manifest))
        broken["basis"]["romset_hash"] = "rom"
        assert any("must be a SHA-256" in error for error in validate(broken, evidence, root))
        pack["basis"]["romset_hash"] = "a" * 64
        broken = copy.deepcopy(pack)
        broken["assets"][0]["status"] = "verified"
        assert any("invalid status" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["assets"][0]["claims"]["source_ranges"] = "candidate"
        assert any("require validated claims: source_ranges" in error
                   for error in validate(broken, evidence, root))
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
        broken["assets"][0]["evidence_ids"] = ["capture-v1", "capture-v1"]
        assert any("evidence_ids must be unique" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        broken["assets"][0]["verifiers"] = ["verify-fighter", "verify-fighter"]
        assert any("verifiers must be unique" in error for error in validate(broken, evidence, root))
        broken = copy.deepcopy(pack)
        shared = copy.deepcopy(broken["assets"][0])
        shared["id"] = "fighter-alias"
        broken["assets"].append(shared)
        assert any("payload is shared" in error for error in validate(broken, evidence, root))
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
        loop = root / "loop.glb"
        loop.symlink_to(loop)
        broken = copy.deepcopy(pack)
        broken["assets"][0]["payload"] = "loop.glb"
        assert any("missing payload" in error for error in validate(broken, evidence, root))
        local_link = root / "local-link.glb"
        local_link.symlink_to(payload)
        broken = copy.deepcopy(pack)
        broken["assets"][0]["payload"] = "local-link.glb"
        assert any("missing payload" in error for error in validate(broken, evidence, root))
        pack_document = root / "pack.json"
        evidence_document = root / "evidence.json"
        pack_document.write_text(json.dumps(pack), encoding="utf-8")
        evidence_document.write_text(json.dumps(evidence), encoding="utf-8")
        linked_pack = root / "linked-pack.json"
        linked_pack.symlink_to(pack_document)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--manifest", str(linked_pack),
             "--evidence-manifest", str(evidence_document), "--root", str(root)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode != 0
        assert "asset pack path must not be a symlink" in cli_result.stdout
        malformed_evidence = root / "malformed-evidence.json"
        malformed_evidence.write_text("{invalid\n", encoding="utf-8")
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--manifest", str(pack_document),
             "--evidence-manifest", str(malformed_evidence), "--root", str(root)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode != 0
        assert "unable to read validation document" in cli_result.stdout
        outside_pack = root.parent / "outside-pack.json"
        outside_pack.write_text(json.dumps(pack), encoding="utf-8")
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--manifest", str(outside_pack),
             "--evidence-manifest", str(evidence_document), "--root", str(root)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode != 0
        assert "asset pack path escapes root" in cli_result.stdout
        broken = copy.deepcopy(pack)
        broken["assets"][0]["verifier_results"]["stale-verifier"] = "pass"
        assert any("passing verifier_results" in error for error in validate(broken, evidence, root))
    print("PASS: evidence asset pack validates claims, hashes, and evidence IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
