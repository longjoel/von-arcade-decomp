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
             "status": "observed", "path": "/assets/model.gltf", "sourceTrace": "trace"},
            {"id": "reference", "displayName": "Reference", "category": "props",
             "status": "reference-capture", "path": "/assets/model.gltf", "sourceTrace": "trace"},
        ]}))
        subprocess.run(["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
                        "--output", output, "--root", root], check=True)
        catalog = json.loads(output.read_text())
        assert catalog["counts"]["observed"] == 1
        assert catalog["counts"]["reference-capture"] == 1
        outside = root.parent / f"outside-catalog-{root.name}.json"
        result = subprocess.run(
            ["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public",
             "--output", outside, "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "output path escapes root" in result.stdout
        traversal = root / "traversal.json"
        traversal.write_text(json.dumps({"assets": [{"path": "../escape.gltf"}]}))
        result = subprocess.run(
            ["python3", TOOL, "--manifest", traversal, "--asset-root", root / "public",
             "--output", root / "bad.json", "--root", root],
            capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "escapes asset root" in result.stdout
    print("PASS: asset catalog build")


if __name__ == "__main__":
    main()
