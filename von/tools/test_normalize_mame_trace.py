#!/usr/bin/env python3
"""Contract tests for normalized ordered MAME events."""

from __future__ import annotations

import json
import gzip
import tempfile
from pathlib import Path

from normalize_mame_trace import ndjson_event, read_trace, select_events, summary, trigger_window


def main() -> int:
    event = ndjson_event("[00:01] vonj_copro_fifo: pc=00001234 data=000000ff", 0)
    assert event == {"seq": 0, "kind": "vonj_copro_fifo", "pc": 0x1234, "data": 0xFF}
    sample = ndjson_event("sample=3 frame=12 time=0.25 pc=0001bc50 read=00000000", 1)
    assert sample["kind"] == "audio-queue-sample"
    assert sample["time"] == 0.25
    assert sample["pc"] == 0x1BC50
    assert ndjson_event("not an event", 2) is None
    selected = select_events([event, sample], max_events=1, event_kinds={"vonj_copro_fifo"})
    assert len(selected) == 1 and selected[0]["seq"] == 0
    assert select_events([event], pc_min=0x2000) == []
    trigger_events = [
        {"kind": "boot", "name": "before"},
        {"kind": "checkpoint", "name": "scheduler"},
        {"kind": "mmio-write", "address": "0x10"},
        {"kind": "mmio-write", "address": "0x20"},
    ]
    window, found = trigger_window(trigger_events, "checkpoint", "scheduler", 2)
    assert found and window == trigger_events[1:3]
    assert trigger_window(trigger_events, "checkpoint", "missing", 2) == ([], False)
    assert select_events(trigger_events, trigger_kind="checkpoint", trigger_name="scheduler",
                         window_events=2) == trigger_events[1:3]
    try:
        trigger_window(trigger_events, "checkpoint")
    except ValueError as error:
        assert "window_events" in str(error)
    else:
        raise AssertionError("unbounded trigger window was accepted")
    report = summary([event, sample], Path("trace.log"), max_events=1,
                     event_kinds={"vonj_copro_fifo"})
    assert report["event_count"] == 1
    assert report["event_counts"] == {"vonj_copro_fifo": 1}
    assert report["first_event"]["kind"] == "vonj_copro_fifo"
    assert report["filters"]["event_kinds"] == ["vonj_copro_fifo"]
    trigger_report = summary(trigger_events, Path("trace.log"), trigger_kind="checkpoint",
                             trigger_name="scheduler", window_events=2)
    assert trigger_report["event_count"] == 2
    assert trigger_report["filters"]["trigger_found"] is True
    report = summary([event], Path("trace.log"), provenance={
        "capture_id": "capture-v1", "objective": "pilot",
        "stimulus": {"kind": "bounded-trace", "seconds": 1}, "artifact": "trace.log",
    })
    assert report["provenance"]["capture_id"] == "capture-v1"
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "events.ndjson"
        path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        assert json.loads(path.read_text(encoding="utf-8"))["kind"] == "vonj_copro_fifo"
        compressed = Path(directory) / "events.ndjson.gz"
        with gzip.open(compressed, "wt", encoding="utf-8") as stream:
            stream.write(json.dumps(event) + "\n")
        assert read_trace(compressed).strip() == json.dumps(event)
    print("PASS: MAME trace normalizer emits ordered NDJSON events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
