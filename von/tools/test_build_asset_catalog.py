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
        subprocess.run(["python3", TOOL, "--manifest", manifest, "--asset-root", root / "public", "--output", output], check=True)
        catalog = json.loads(output.read_text())
        assert catalog["counts"] == {"verified": 0, "candidate": 1, "rejected": 0}
        assert catalog["assets"][0]["geometry"] == {"nodes": 1, "meshes": 1, "materials": 0, "images": 0}
    print("PASS: asset catalog build")


if __name__ == "__main__":
    main()
