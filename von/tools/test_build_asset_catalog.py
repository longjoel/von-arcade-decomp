import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from capture_manifest import directory_sha256, entry

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/build_asset_catalog.py"


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); assets = root / "public/assets"; assets.mkdir(parents=True)
        (assets / "model.gltf").write_text(json.dumps({"asset": {"version": "2.0"}, "nodes": [{}], "meshes": [{}]}))
        for name in ("cfg", "nvram", "state"):
            (assets / name).mkdir()
        input_path = assets / "rom-manifest.json"
        input_path.write_text('{"rom":"fixture"}\n', encoding="utf-8")
        artifact_path = assets / "events.ndjson"
        artifact_path.write_text('{"seq":1}\n', encoding="utf-8")
        coverage_path = assets / "coverage.json"
        coverage_path.write_text(json.dumps({
            "capture_id": "capture-v1", "tier": "A",
            "edge_semantics": "possible_static_edges", "phase": "startup",
        }), encoding="utf-8")
        capture = {
            "schema_version": 1, "id": "capture-v1", "objective": "catalog-fixture",
            "hypothesis": "the fixture capture is reproducible",
            "expected_discriminator": "the coverage report has the capture id",
            "stimulus": {"kind": "input-free-attract", "seconds": 1, "phase": "startup"},
            "checkpoints": ["reset", "startup"],
            "configuration": {"set": "vonj", "mame_revision": "a" * 40,
                               "patch_profile": "none", "execution_engine": "interpreter"},
            "command": ["mame", "vonj", "-cfg_directory", "cfg",
                         "-nvram_directory", "nvram", "-state_directory", "state",
                         "-seconds_to_run", "1"],
            "isolation": {"cfg_directory": "cfg", "nvram_directory": "nvram",
                          "state_directory": "state"},
            "coverage_report": "coverage.json",
            "inputs": [entry(input_path, assets)],
            "artifacts": [entry(artifact_path, assets), entry(coverage_path, assets)],
        }
        for field in ("cfg_directory", "nvram_directory", "state_directory"):
            capture["isolation"][f"{field}_sha256"] = directory_sha256(
                assets / capture["isolation"][field])
        (assets / "capture.json").write_text(json.dumps(capture), encoding="utf-8")
        capture_sha = hashlib.sha256((assets / "capture.json").read_bytes()).hexdigest()
        (assets / "evidence.json").write_text(json.dumps({
            "id": "capture-v1", "canonical": True, "outcome": "pass",
            "capture_manifest": "/assets/capture.json",
            "capture_manifest_sha256": capture_sha,
        }), encoding="utf-8")
        manifest = root / "manifest.json"; output = root / "catalog.json"
        manifest.write_text(json.dumps({"assets": [{"id": "model", "displayName": "Model", "category": "props",
            "status": "candidate", "path": "/assets/model.gltf", "sourceTrace": "trace"}]}))
        subprocess.run(["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
                        "--output", output, "--root", root], check=True)
        catalog = json.loads(output.read_text())
        assert catalog["counts"] == {
            "legacy-unreviewed": 0,
            "candidate": 1,
            "observed": 0,
            "validated": 0,
            "rejected": 0,
            "reference-capture": 0,
        }
        assert catalog["assets"][0]["geometry"] == {"nodes": 1, "meshes": 1, "materials": 0, "images": 0}
        manifest.write_text(json.dumps({"assets": [
            {"id": "model", "displayName": "Model", "category": "props",
             "status": "observed", "path": "/assets/model.gltf", "sourceTrace": "trace",
             "evidencePath": "/assets/evidence.json"},
            {"id": "reference", "displayName": "Reference", "category": "props",
             "status": "reference-capture", "path": "/assets/model.gltf", "sourceTrace": "trace",
             "evidencePath": "/assets/evidence.json"},
        ]}))
        subprocess.run(["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
                        "--output", output, "--root", root], check=True)
        catalog = json.loads(output.read_text())
        assert catalog["counts"]["observed"] == 1
        assert catalog["counts"]["reference-capture"] == 1
        valid_manifest = manifest.read_text()
        manifest.write_text(json.dumps({"assets": [
            {"id": "model", "displayName": "Model", "category": "props",
             "status": "observed", "path": "/assets/model.gltf", "sourceTrace": "trace"},
        ]}))
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "missing evidencePath for status 'observed'" in result.stdout
        manifest.write_text(json.dumps({"assets": [
            {"id": "model", "displayName": "Model", "category": "props",
             "status": "observed", "path": "/assets/model.gltf", "sourceTrace": "trace",
             "evidencePath": "/assets/evidence.json"},
        ]}))
        (assets / "evidence.json").write_text(json.dumps({
            "id": "capture-v1", "canonical": True, "outcome": "pass",
            "capture_manifest": "/assets/missing-capture.json",
            "capture_manifest_sha256": capture_sha,
        }), encoding="utf-8")
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "missing capture manifest" in result.stdout
        (assets / "evidence.json").write_text(json.dumps({
            "id": "capture-v1", "canonical": True, "outcome": "pass",
            "capture_manifest": "/assets/capture.json",
            "capture_manifest_sha256": "0" * 64,
        }), encoding="utf-8")
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "capture manifest hash mismatch" in result.stdout
        (assets / "evidence.json").write_text(json.dumps({
            "id": "capture-v1", "canonical": True, "outcome": "pass",
            "capture_manifest": "/assets/capture.json",
            "capture_manifest_sha256": capture_sha,
        }), encoding="utf-8")
        invalid_capture = json.loads((assets / "capture.json").read_text(encoding="utf-8"))
        invalid_capture["hypothesis"] = ""
        (assets / "capture.json").write_text(json.dumps(invalid_capture), encoding="utf-8")
        invalid_capture_sha = hashlib.sha256((assets / "capture.json").read_bytes()).hexdigest()
        (assets / "evidence.json").write_text(json.dumps({
            "id": "capture-v1", "canonical": True, "outcome": "pass",
            "capture_manifest": "/assets/capture.json",
            "capture_manifest_sha256": invalid_capture_sha,
        }), encoding="utf-8")
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "invalid capture manifest" in result.stdout
        assert "missing capture hypothesis" in result.stdout
        (assets / "capture.json").write_text(json.dumps(capture), encoding="utf-8")
        capture_sha = hashlib.sha256((assets / "capture.json").read_bytes()).hexdigest()
        (assets / "evidence.json").write_text(json.dumps({
            "id": "capture-v1", "canonical": True, "outcome": "pass",
            "capture_manifest": "/assets/capture.json",
            "capture_manifest_sha256": capture_sha,
        }), encoding="utf-8")
        manifest.write_text(json.dumps({"assets": [
            {"id": "model", "displayName": "Model", "category": "props",
             "status": "candidate", "path": "/assets/model.gltf", "sourceTrace": "trace"},
            {"id": "model", "displayName": "Duplicate", "category": "props",
             "status": "candidate", "path": "/assets/model.gltf", "sourceTrace": "trace"},
        ]}))
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "duplicate asset id" in result.stdout
        manifest.write_text(json.dumps({"assets": [
            {"id": "model", "category": "props",
             "status": "candidate", "path": "/assets/model.gltf", "sourceTrace": "trace"},
        ]}))
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "missing asset displayName" in result.stdout
        manifest.write_text(json.dumps({"assets": [
            {"id": "model", "displayName": "Model", "category": "props",
             "status": "verified", "path": "/assets/model.gltf", "sourceTrace": "trace"},
        ]}))
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "unsupported asset status" in result.stdout
        manifest.write_text(json.dumps({"assets": [
            {"id": "model", "displayName": "Model", "category": "props",
             "path": "/assets/model.gltf", "sourceTrace": "trace"},
        ]}))
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "unsupported asset status" in result.stdout
        manifest.write_text(valid_manifest)
        outside = root.parent / f"outside-catalog-{root.name}.json"
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", outside, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "output path escapes root" in result.stdout
        traversal = root / "traversal.json"
        traversal.write_text(json.dumps({"assets": [{
            "id": "escape", "displayName": "Escape", "category": "props",
            "status": "candidate", "path": "../escape.gltf",
        }]}))
        result = subprocess.run(
            ["python3", TOOL, "--manifest", traversal, "--asset-root", root / "public",
             "--output", root / "bad.json", "--root", root],
            capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "escapes asset root" in result.stdout
    print("PASS: asset catalog build")


if __name__ == "__main__":
    main()
