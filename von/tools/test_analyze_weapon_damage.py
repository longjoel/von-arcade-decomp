#!/usr/bin/env python3
"""Regression test for the analyze-weapon-damage analyzer.

Builds a tiny synthetic weapon log with one discrete hit, one sustained drain,
one tiny blip and one round transition, then checks that the tool recovers the
known timer starts, event shapes and per-slot attribution. Also checks the
legacy four-cell layout auto-detection and the JSON/markdown outputs.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/analyze-weapon-damage"


def working_series(last: int = 110):
    values = {}
    for frame in range(1, last + 1):
        if frame < 12:
            value = 100
        elif frame < 40:
            value = 70
        elif frame == 40:
            value = 62
        elif frame == 41:
            value = 54
        elif frame == 42:
            value = 46
        elif frame < 70:
            value = 38
        elif frame < 90:
            value = 30
        else:
            value = 0
        values[frame] = value
    return values


def live_series(last: int = 110):
    values = {}
    for frame in range(1, last + 1):
        if frame < 12:
            value = 100
        elif frame == 12:
            value = 92
        elif frame == 13:
            value = 84
        elif frame == 14:
            value = 77
        elif frame < 40:
            value = 70
        elif frame == 40:
            value = 62
        elif frame == 41:
            value = 54
        elif frame == 42:
            value = 46
        elif frame < 70:
            value = 38
        elif frame == 70:
            value = 34
        elif frame < 90:
            value = 30
        else:
            value = 0
        values[frame] = value
    return values


def build_new_fixture(path: Path):
    working = working_series()
    live = live_series()
    lines = []
    for frame in range(1, 111):
        timers = [0, 0, 0]
        if frame == 5:
            timers[0] = 10
        elif frame > 5:
            timers[0] = max(0, 15 - frame)
        if frame == 30:
            timers[1] = 300
        elif frame > 30:
            timers[1] = 330 - frame
        if frame == 60:
            timers[2] = 300
        elif frame > 60:
            timers[2] = 360 - frame
        snapshot = 200 if frame >= 90 else 100
        opponent = 500
        hp = [snapshot, working[frame], live[frame], opponent, 500, 500]
        lines.append(
            "weapon: f%d resources=00,00,00 availability=01,01,01 "
            "timers=%04x,%04x,%04x hp=%s"
            % (frame, timers[0], timers[1], timers[2], ",".join("%04x" % v for v in hp))
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_legacy_fixture(path: Path):
    live = live_series(40)
    lines = []
    for frame in range(1, 41):
        hp = [live[frame], 500, 10, 20]
        lines.append(
            "weapon: f%d resources=00,00,00 availability=01,01,01 "
            "timers=0000,0000,0000 hp=%s"
            % (frame, ",".join("%04x" % v for v in hp))
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def event_at(report, frame):
    for event in report["live_events"]:
        if event["start"] == frame:
            return event
    raise AssertionError(f"no live event starting at f{frame}: {report['live_events']}")


def run_tool(log, *extra):
    result = subprocess.run(
        ["python3", str(TOOL), str(log), *extra],
        capture_output=True,
        text=True,
        check=True,
    )
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-weapon-damage-") as directory:
        root = Path(directory)
        log = root / "record.log"
        json_path = root / "out.json"
        md_path = root / "out.md"
        build_new_fixture(log)

        result = run_tool(log, "--json", str(json_path), "--markdown", str(md_path))
        report = json.loads(json_path.read_text(encoding="utf-8"))

        assert report["layout"] == "new", report["layout"]
        assert report["timer_starts"]["right"] == [5], report["timer_starts"]
        assert report["timer_starts"]["left"] == [30], report["timer_starts"]
        assert report["timer_starts"]["both"] == [60], report["timer_starts"]

        discrete = event_at(report, 12)
        assert discrete["damage"] == 30, discrete
        assert discrete["shape"] == "discrete", discrete
        assert discrete["attributed_slot"] == 1, discrete
        sustained = event_at(report, 40)
        assert sustained["damage"] == 32, sustained
        assert sustained["shape"] == "sustained", sustained
        assert sustained["attributed_slot"] == 2, sustained
        tiny = event_at(report, 70)
        assert tiny["damage"] == 8, tiny
        assert tiny["shape"] == "tiny", tiny
        transition = event_at(report, 90)
        assert transition["shape"] == "transition", transition

        assert report["per_slot"]["1"]["hit_sizes"] == [30], report["per_slot"]
        assert report["per_slot"]["2"]["hit_sizes"] == [32], report["per_slot"]
        assert report["per_slot"]["3"]["hit_sizes"] == [8], report["per_slot"]
        assert report["per_slot"]["1"]["fires"] == 1
        assert report["per_slot"]["2"]["fires"] == 1
        assert report["per_slot"]["3"]["fires"] == 1
        assert 0.0 < report["attribution_window_coverage"] <= 1.0

        assert "per-slot attribution" in result.stdout
        markdown = md_path.read_text(encoding="utf-8")
        assert "| slot | weapon |" in markdown, markdown
        assert "| 1 | right | 1 | 1 | [30]" in markdown, markdown

        legacy_log = root / "legacy.log"
        build_legacy_fixture(legacy_log)
        legacy_json = root / "legacy.json"
        run_tool(legacy_log, "--json", str(legacy_json))
        legacy = json.loads(legacy_json.read_text(encoding="utf-8"))
        assert legacy["layout"] == "legacy", legacy["layout"]
        assert legacy["live_cell"] == 0, legacy["live_cell"]

    print("PASS: analyze-weapon-damage timer/event/slot attribution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
