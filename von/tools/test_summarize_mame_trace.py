#!/usr/bin/env python3
"""Regression test for streaming MAME trace summaries and gzip archives."""

from __future__ import annotations

import gzip
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/summarize_mame_trace.py"


def main() -> int:
    original = (
        "Soft reset\n"
        "[:] vonj_palette_write: offset=0010 data=0000\n"
        "[:] vonj_tile_write: pc=0001d3a0 offset=09c8 data=8123\n"
        + "P1 M2COMM: diag rx failure error=Resource temporarily unavailable\n" * 3
    ).encode()
    with tempfile.TemporaryDirectory(prefix="von-trace-summary-") as directory:
        trace = Path(directory) / "fixture.trace"
        trace.write_bytes(original)
        subprocess.run(["python3", TOOL, trace, "--archive"], check=True)
        report = json.loads((Path(str(trace) + ".summary.json")).read_text())
        if report["lines"] != 6 or report["event_counts"] != {
            "unstructured": 4, "vonj_palette_write": 1, "vonj_tile_write": 1
        }:
            raise SystemExit(f"unexpected summary counts: {report!r}")
        if not report["collapsed_runs"] or report["collapsed_runs"][0]["lines"] != 3:
            raise SystemExit("failed to collapse repeated diagnostic run")
        archive = Path(str(trace) + ".gz")
        if trace.exists() or gzip.open(archive, "rb").read() != original:
            raise SystemExit("gzip archive did not preserve raw trace")
    print("PASS: streaming trace summary, run collapse, checksum metadata, and gzip archive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
