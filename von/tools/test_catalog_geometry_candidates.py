import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/catalog_geometry_candidates.py"


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); trace = root / "trace.log"; output = root / "candidates.json"
        trace.write_text("\n".join([
            "[:] vonj_geometry_matrix: time=1 m=1,0,0,0,1,0,0,0,1 t=0,0,0",
            "[:] vonj_geometry_object: time=1 tpa=0 tha=0 oba=00000010 count=0 mode=3 source=polygon-rom opcode=00800101",
            "[:] vonj_geometry_object: time=1 tpa=0 tha=0 oba=00000020 count=0 mode=3 source=polygon-rom opcode=00800101",
            "[:] vonj_geometry_matrix: time=1 m=1,0,0,0,1,0,0,0,1 t=30,0,0",
            "[:] vonj_geometry_object: time=1 tpa=0 tha=0 oba=00000030 count=0 mode=3 source=polygon-rom opcode=00800101",
        ]) + "\n")
        subprocess.run(["python3", TOOL, "--trace", trace, "--time", "1", "--output", output,
                        "--root", root], check=True)
        data = json.loads(output.read_text())
        assert [(entry["start_slot"], entry["object_count"]) for entry in data["candidates"]] == [(0, 2), (2, 1)]
        outside = root.parent / "outside-geometry-candidates.json"
        result = subprocess.run(
            ["python3", TOOL, "--trace", trace, "--time", "1", "--output", outside,
             "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "output path escapes root" in result.stdout
    print("PASS: geometry candidate catalog")


if __name__ == "__main__":
    main()
