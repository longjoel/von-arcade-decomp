#!/usr/bin/env python3
"""Contract tests for normalized ordered MAME events."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from normalize_mame_trace import ndjson_event, select_events, summary


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
    report = summary([event, sample], Path("trace.log"), max_events=1,
                     event_kinds={"vonj_copro_fifo"})
    assert report["event_count"] == 1
    assert report["event_counts"] == {"vonj_copro_fifo": 1}
    assert report["first_event"]["kind"] == "vonj_copro_fifo"
    assert report["filters"]["event_kinds"] == ["vonj_copro_fifo"]
    report = summary([event], Path("trace.log"), provenance={
        "capture_id": "capture-v1", "objective": "pilot",
        "stimulus": {"kind": "bounded-trace", "seconds": 1}, "artifact": "trace.log",
    })
    assert report["provenance"]["capture_id"] == "capture-v1"
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "events.ndjson"
        path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        assert json.loads(path.read_text(encoding="utf-8"))["kind"] == "vonj_copro_fifo"
    print("PASS: MAME trace normalizer emits ordered NDJSON events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
