#!/usr/bin/env python3
"""Contract tests for the frames JSON extractor (synthetic data only)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
TRACE = """\
[:] vonj_geometry_matrix: time=138.011576 m=1,0,0,0,1,0,0,0,1 t=2.0,-32.0,53.0
[:] vonj_geometry_object: time=138.011576 tpa=00401e08 tha=00401e50 oba=0084e1d1 count=00000000 mode=3 source=polygon-rom opcode=00800101
[:] vonj_geometry_object: time=138.011576 tpa=00401e08 tha=00401e50 oba=0084e1d2 count=00000000 mode=1 source=polygon-rom opcode=00800101
[:] vonj_geometry_object: time=138.011576 tpa=00401e08 tha=00401e50 oba=0084e1d3 count=00000000 mode=3 source=polygon-ram opcode=00800101
[:] vonj_geometry_matrix: time=138.028960 m=1,0,0,0,1,0,0,0,1 t=3.0,-31.0,52.0
[:] vonj_geometry_object: time=138.028960 tpa=00401e08 tha=00401e50 oba=0084e1d1 count=00000000 mode=3 source=polygon-rom opcode=00800101
"""


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "trace.log").write_text(TRACE)
        out = td / "frames.json"
        r = subprocess.run(
            [sys.executable, str(TOOLS / "extract_frames_json.py"),
             "--trace", str(td / "trace.log"), "--output", str(out)],
            capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        frames = json.loads(out.read_text())
        assert len(frames) == 2, frames.keys()
        e = frames["138.011576"][0]
        assert e[0] == "0084e1d1", e
        assert e[1] == 0x401e08 and e[2] == 0x401e50, e[1:3]
        assert e[3:12] == [1, 0, 0, 0, 1, 0, 0, 0, 1], e[3:12]
        assert e[12:15] == [2.0, -32.0, 53.0], e[12:]
        # mode-1 and polygon-ram objects are dropped.
        assert len(frames["138.011576"]) == 1, frames["138.011576"]
        # Window filter keeps only the second frame.
        out2 = td / "frames2.json"
        r = subprocess.run(
            [sys.executable, str(TOOLS / "extract_frames_json.py"),
             "--trace", str(td / "trace.log"), "--output", str(out2),
             "--t0", "138.02", "--t1", "138.03"],
            capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        frames2 = json.loads(out2.read_text())
        assert list(frames2) == ["138.028960"], frames2.keys()
    print("frames extractor tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
