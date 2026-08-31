#!/usr/bin/env python3
"""Regression test for extracting an instanced static ROM geometry assembly."""

from __future__ import annotations

import json
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/export_geometry_frame_gltf.py"


def main() -> int:
    trace_text = (
        "[:] vonj_geometry_matrix: time=1.0 m=1,0,0,0,1,0,0,0,1 t=0,0,0\n"
        "[:] vonj_geometry_object: time=1.0 tpa=00000000 tha=00000000 "
        "oba=00000000 count=00000000 mode=3 source=polygon-rom\n"
        "[:] vonj_geometry_object: time=1.0 tpa=00000000 tha=00000000 "
        "oba=00000000 count=00000000 mode=3 source=polygon-rom\n"
    )
    with tempfile.TemporaryDirectory(prefix="von-frame-export-") as directory:
        root = Path(directory)
        rom = root / "geometry-rom.bin"
        trace = root / "trace.log"
        output = root / "assembly.gltf"
        rom.write_bytes(struct.pack(
            "<6fI3I3f3I",
            0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
            2, 0, 0, 0, 0.0, 1.0, 0.0, 0, 0, 0,
        ))
        trace.write_text(trace_text)
        subprocess.run([
            "python3", TOOL, "--trace", trace, "--rom", rom, "--output", output,
            "--time", "1", "--start-object", "1", "--max-objects", "1",
        ], check=True)
        document = json.loads(output.read_text())
        if (document["extras"]["object_slots"], document["extras"]["object_start"],
                len(document["nodes"]), len(document["meshes"])) != (1, 1, 1, 1):
            raise SystemExit("static assembly slice metadata or geometry is wrong")
        if document["nodes"][0]["name"] != "slot_001_oba_00000000":
            raise SystemExit("original submission slot was not retained")
    print("PASS: static ROM geometry assembly glTF export")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
