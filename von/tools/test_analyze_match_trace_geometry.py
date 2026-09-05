#!/usr/bin/env python3
"""Contract test for the bounded post-start geometry trace summary."""

from pathlib import Path
import subprocess
import sys
import tempfile

from analyze_match_trace_geometry import summarize

TRACE = """\
[:] vonj_geometry_matrix: time=1.0 m=1,0,0,0,1,0,0,0,1 t=0,0,0
[:] vonj_geometry_object: time=1.0 tpa=1 tha=2 oba=00000001 count=00000001 mode=3 source=polygon-rom opcode=00800101
[:] vonj_geometry_matrix: time=2.0 m=2,0,0,0,2,0,0,0,2 t=3,4,5
[:] vonj_geometry_object: time=2.0 tpa=1 tha=2 oba=00000002 count=00000001 mode=3 source=polygon-rom opcode=00800101
[:] vonj_geometry_object: time=2.0 tpa=1 tha=2 oba=00000003 count=00000001 mode=3 source=tile opcode=00000000
"""

TOOL = Path(__file__).resolve().parent / "analyze_match_trace_geometry.py"

with tempfile.TemporaryDirectory(prefix="von-match-trace-") as directory:
    path = Path(directory) / "trace.log"
    path.write_text(TRACE)
    result = summarize(path, 2.0, 2)

assert result["post_start_objects"] == 2
assert result["post_start_unique_oba"] == 2
assert result["oba_with_stable_tpa_tha"] == 2
assert result["oba_with_multiple_tpa_tha"] == 0
assert result["maximum_submissions_per_oba"] == 1
assert result["post_start_matrices"] == 1
assert result["post_start_objects_with_latest_matrix"] == 2
assert result["matrix_stream_saturated"] is True
assert result["objects_by_source"] == {"polygon-rom": 1, "tile": 1}
assert result["opcodes"] == {"00000000": 1, "00800101": 1}
with tempfile.TemporaryDirectory(prefix="von-match-trace-cli-") as directory:
    root = Path(directory)
    trace = root / "trace.log"
    trace.write_text(TRACE)
    outside = root.parent / "outside-match-trace.json"
    cli_result = subprocess.run(
        [sys.executable, str(TOOL), "--trace", str(trace), "--output", str(outside),
         "--root", str(root)], capture_output=True, text=True, check=False)
    assert cli_result.returncode == 1
    assert "output path escapes root" in cli_result.stdout
print("PASS: bounded post-start geometry trace summary")
