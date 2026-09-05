import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/build_asset_catalog.py"


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); assets = root / "public/assets"; assets.mkdir(parents=True)
        (assets / "model.gltf").write_text(json.dumps({"asset": {"version": "2.0"}, "nodes": [{}], "meshes": [{}]}))
        (assets / "evidence.json").write_text(json.dumps({"id": "capture-v1", "canonical": True,
                                                          "outcome": "pass"}), encoding="utf-8")
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
        (assets / "evidence.json").write_text(json.dumps({"id": "capture-v1", "canonical": False,
                                                          "outcome": "pass"}), encoding="utf-8")
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "evidence must be canonical" in result.stdout
        (assets / "evidence.json").write_text(json.dumps({"id": "capture-v1", "canonical": True,
                                                          "outcome": "fail"}), encoding="utf-8")
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", output, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "outcome 'pass'" in result.stdout
        (assets / "evidence.json").write_text(json.dumps({"id": "capture-v1", "canonical": True,
                                                          "outcome": "pass"}), encoding="utf-8")
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
