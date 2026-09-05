from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).parents[2]
TOOL = ROOT / "von/tools/compare_geometry_parser_opcode_prefix.py"


def test_opcode_prefix_accepts_matching_order():
    lines = "\n".join(
        f"vonj_geometry_opcode: time=1.{i:06d} read=00010000 opcode={value:08x}"
        for i, value in enumerate((0x0B001616, 0x03800707, 0x04000808))
    )
    with tempfile.TemporaryDirectory() as directory:
        first = Path(directory) / "first.log"
        second = Path(directory) / "second.log"
        first.write_text(lines + "\n", encoding="utf-8")
        second.write_text(lines + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(TOOL), "--original", str(first),
             "--reconstructed", str(second), "--events", "3"],
            capture_output=True, text=True, check=False,
        )
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_opcode_prefix_reports_first_divergence():
    with tempfile.TemporaryDirectory() as directory:
        first = Path(directory) / "first.log"
        second = Path(directory) / "second.log"
        first.write_text("vonj_geometry_opcode: opcode=0b001616\n", encoding="utf-8")
        second.write_text("vonj_geometry_opcode: opcode=03800000\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(TOOL), "--original", str(first),
             "--reconstructed", str(second), "--events", "1"],
            capture_output=True, text=True, check=False,
        )
    assert result.returncode == 1
    assert "original=0b001616 reconstructed=03800000" in result.stdout

