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
        ordered_trace = root / "ordered-trace.log"
        ordered_lines = []
        sequence = 0
        for time in (1.0, 1.1, 1.2):
            for oba in (0x10, 0x20):
                ordered_lines.append(f"[:] vonj_geometry_object: seq={sequence} time={time} tpa=0 tha=0 oba={oba:08x} count=0 mode=3 source=polygon-rom opcode=00800101")
                sequence += 1
        ordered_trace.write_text("\n".join(ordered_lines) + "\n")
        subprocess.run(["python3", TOOL, "--trace", ordered_trace, "--time", "1", "--start-slot", "0",
                        "--object-count", "2", "--minimum-stable-frames", "3",
                        "--require-ordered-sequence", "--output", output], check=True)
        evidence = json.loads(output.read_text())
        assert evidence["sequence_validated"] is True
        result = subprocess.run(["python3", TOOL, "--trace", trace, "--time", "1", "--start-slot", "0",
                                 "--object-count", "2", "--minimum-stable-frames", "3",
                                 "--require-ordered-sequence", "--output", output],
                                capture_output=True, text=True, check=False)
        assert result.returncode != 0 and "validation" in result.stderr
    print("PASS: geometry assembly verification")


if __name__ == "__main__":
    main()
