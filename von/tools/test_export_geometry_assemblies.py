#!/usr/bin/env python3
"""Regression test for spatial grouping of static ROM geometry assemblies."""
from __future__ import annotations
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/export_geometry_assemblies.py"
def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); rom = root / "rom.bin"; trace = root / "trace.log"; output = root / "out"
        rom.write_bytes(struct.pack("<6fI3I3f3I", 0,0,0, 1,0,0, 2,0,0,0, 0,1,0, 0,0,0))
        lines = []
        for x in (0, 1, 30, 31):
            lines += [f"[:] vonj_geometry_matrix: time=1 m=1,0,0,0,1,0,0,0,1 t={x},0,0",
                      "[:] vonj_geometry_object: time=1 tpa=0 tha=0 oba=00000000 count=0 mode=3 source=polygon-rom"]
        trace.write_text("\n".join(lines) + "\n")
        subprocess.run(["python3", TOOL, "--trace", trace, "--rom", rom, "--output-dir", output,
                        "--time", "1", "--min-objects", "4", "--distance", "10", "--root", root], check=True)
        manifest = json.loads((output / "assemblies.json").read_text())
        if [(x["start_slot"], x["object_count"]) for x in manifest["assemblies"]] != [(0, 2), (2, 2)]:
            raise SystemExit("spatial assembly partition mismatch")
        outside = root.parent / "outside-geometry-assemblies"
        result = subprocess.run(
            ["python3", TOOL, "--trace", trace, "--rom", rom, "--output-dir", outside,
             "--root", root], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "output directory path escapes root" in result.stdout
    print("PASS: spatial ROM assembly extraction")
if __name__ == "__main__": main()
