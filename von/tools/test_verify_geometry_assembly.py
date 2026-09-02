import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/verify_geometry_assembly.py"


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); trace = root / "trace.log"; output = root / "evidence.json"
        lines = []
        for time in (1.0, 1.1, 1.2):
            for oba in (0x10, 0x20):
                lines.append(f"[:] vonj_geometry_object: time={time} tpa=0 tha=0 oba={oba:08x} count=0 mode=3 source=polygon-rom opcode=00800101")
        trace.write_text("\n".join(lines) + "\n")
        subprocess.run(["python3", TOOL, "--trace", trace, "--time", "1", "--start-slot", "0",
                        "--object-count", "2", "--minimum-stable-frames", "3", "--output", output], check=True)
        evidence = json.loads(output.read_text())
        assert evidence["status"] == "verified" and evidence["obas"] == ["00000010", "00000020"]
        assert evidence["stable_frame_count"] == 3
    print("PASS: geometry assembly verification")


if __name__ == "__main__":
    main()
