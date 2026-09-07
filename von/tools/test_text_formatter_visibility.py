#!/usr/bin/env python3
"""Contract tests for the text-formatter visibility analyzer."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/analyze_text_formatter_visibility.py"


LEDGER = {
    "images": [
        {
            "name": "maincpu",
            "work_units": [
                {
                    "id": "maincpu.text-string-byte-dispatch",
                    "classification": "code",
                    "stage": "trace-validated",
                    "ranges": [{"start": "0x0001d1b0", "end": "0x0001d1c0"}],
                },
                {
                    "id": "maincpu.text-general-formatter-boundary",
                    "classification": "code",
                    "stage": "modeled",
                    "ranges": [{"start": "0x0001d800", "end": "0x0001d810"}],
                },
                {
                    "id": "maincpu.other-unit",
                    "classification": "code",
                    "stage": "modeled",
                    "ranges": [{"start": "0x00010000", "end": "0x00010010"}],
                },
            ],
        }
    ]
}


def run(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *argv],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(dir=ROOT) as directory:
        work = Path(directory)
        capture = work / "capture"
        capture.mkdir()
        (capture / "coin_insert-start-pcs.txt").write_text(
            "0001d1b0\n0001d1b4\n00010000\n", encoding="ascii"
        )
        (capture / "coin_insert-end-pcs.txt").write_text("00010004\n", encoding="ascii")
        ledger_path = work / "ledger.json"
        ledger_path.write_text(json.dumps(LEDGER), encoding="utf-8")
        report_path = work / "report.json"

        result = run("--capture-dir", str(capture), "--ledger", str(ledger_path),
                     "--root", str(ROOT), "--json", str(report_path))
        assert result.returncode == 0, result.stdout + result.stderr
        assert "fired=1 [string-byte-dispatch]" in result.stdout, result.stdout
        assert "silent: maincpu.text-general-formatter-boundary [modeled]" in result.stdout

        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["units"] == [
            "maincpu.text-string-byte-dispatch",
            "maincpu.text-general-formatter-boundary",
        ]
        end_phase, start_phase = report["phases"]
        assert start_phase["dump"] == "coin_insert-start-pcs.txt"
        assert [u["fired"] for u in start_phase["units"]] == [True, False]
        assert [u["fired"] for u in end_phase["units"]] == [False, False]
        assert start_phase["units"][0]["visited"] == 2
        assert start_phase["units"][0]["total"] == 4

        missing = run("--capture-dir", str(work / "absent"),
                      "--ledger", str(ledger_path), "--root", str(ROOT))
        assert missing.returncode == 1
        assert "missing capture directory" in missing.stdout

    print("text formatter visibility pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
