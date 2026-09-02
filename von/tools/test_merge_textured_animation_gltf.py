import base64
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/merge_textured_animation_gltf.py"


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        textured = root / "textured.gltf"
        animation = root / "animation.gltf"
        output = root / "merged.gltf"
        payload = base64.b64encode(b"animation-bytes").decode()
        textured.write_text(json.dumps({
            "nodes": [{"name": "slot_000_oba_00000010", "extras": {"geometry_object": {"oba": 16}}}],
            "buffers": [], "bufferViews": [], "accessors": [], "materials": [{"name": "paint"}],
        }))
        animation.write_text(json.dumps({
            "nodes": [{"name": "family_slot_000_oba_00000010"}],
            "buffers": [{"byteLength": 15, "uri": "data:application/octet-stream;base64," + payload}],
            "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 15}],
            "accessors": [{"bufferView": 0, "componentType": 5126, "count": 1, "type": "SCALAR"}],
            "animations": [{"name": "idle", "samplers": [{"input": 0, "output": 0}],
                            "channels": [{"sampler": 0, "target": {"node": 0, "path": "translation"}}]}],
        }))
        subprocess.run(["python3", str(TOOL), "--textured", str(textured), "--animation", str(animation),
                        "--output", str(output)], check=True)
        result = json.loads(output.read_text())
        assert len(result["buffers"]) == 1
        assert result["bufferViews"][0]["buffer"] == 0
        assert result["accessors"][0]["bufferView"] == 0
        assert result["animations"][0]["channels"][0]["target"]["node"] == 0
        assert result["materials"][0]["name"] == "paint"
    print("PASS: textured animation merge")


if __name__ == "__main__":
    main()
