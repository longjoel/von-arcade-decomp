#!/usr/bin/env python3
"""Regression test for the cumulative polygon-ROM triangle animation export."""

from __future__ import annotations

import json
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/export_geometry_triangle_build_gltf.py"


def main() -> int:
    trace_text = (
        "[:] vonj_geometry_matrix: time=1.0 m=1,0,0,0,1,0,0,0,1 t=0,0,0\n"
        "[:] vonj_geometry_object: time=1.0 tpa=00000000 tha=00000000 "
        "oba=00000000 count=00000000 mode=3 source=polygon-rom\n"
    )
    with tempfile.TemporaryDirectory(prefix="von-triangle-build-") as directory:
        root = Path(directory)
        rom = root / "geometry-rom.bin"
        trace = root / "trace.log"
        output = root / "triangle-build.gltf"
        rom.write_bytes(struct.pack(
            "<6fI3I3f3I",
            0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
            2, 0, 0, 0, 0.0, 1.0, 0.0, 0, 0, 0,
        ))
        trace.write_text(trace_text)
        subprocess.run([
            "python3", TOOL, "--trace", trace, "--rom", rom, "--output", output,
            "--max-triangles", "1", "--seconds", "2",
        ], check=True)
        document = json.loads(output.read_text())
        if (len(document["nodes"]), len(document["meshes"]),
                len(document["animations"][0]["channels"])) != (1, 1, 1):
            raise SystemExit("unexpected triangle animation structure")
        if document["extras"]["geometry_filter"] != "mode=3 source=polygon-rom":
            raise SystemExit("geometry filter metadata missing")
        accessor = document["accessors"][2]
        if accessor["min"] != [0.0] or accessor["max"] != [2.0]:
            raise SystemExit("animation input bounds missing")
    print("PASS: polygon-ROM triangle build glTF export")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
