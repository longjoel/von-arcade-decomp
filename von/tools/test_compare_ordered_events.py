#!/usr/bin/env python3
"""Contract tests for ordered causal event comparison."""

from __future__ import annotations

import copy
import tempfile
from pathlib import Path

from compare_ordered_events import capture_provenance_errors, compare, context_errors, load_events


def main() -> int:
    original = [
        {"seq": 1, "time": 1.0, "frame": 1, "kind": "checkpoint", "name": "reset"},
        {"seq": 2, "time": 1.0, "frame": 1, "kind": "checkpoint", "name": "scheduler"},
        {"seq": 3, "time": 1.1, "frame": 2, "kind": "mmio-write", "address": "0x4d", "value": 77},
    ]
    reconstructed = copy.deepcopy(original)
    reconstructed[0]["seq"] = 100
    reconstructed[1]["seq"] = 101
    reconstructed[2]["seq"] = 102
    reconstructed[0]["time"] = 9.0
    reconstructed[0]["source_line"] = 900
    assert compare(original, reconstructed)["outcome"] == "pass"
    calls = original + [
        {"seq": 4, "kind": "indirect-call", "pc": "0x10", "target": "0x20"},
        {"seq": 5, "kind": "indirect-call", "pc": "0x10", "target": "0x20"},
    ]
    call_report = compare(calls, copy.deepcopy(calls))
    assert call_report["confirmed_dynamic_edge_count"] == 1
    assert call_report["observed_indirect_targets"] == ["0x20"]
    assert compare(original, reconstructed)["missed_checkpoints"] == []
    context = {"schema_version": 1, "id": "original-v1", "objective": "pilot", "stimulus": {"kind": "attract", "seconds": 1}}
    reconstructed_context = {"schema_version": 1, "id": "reconstructed-v1", "objective": "pilot", "stimulus": {"kind": "attract", "seconds": 1}}
    contextual = compare(original, reconstructed, context, reconstructed_context)
    assert contextual["context_compatible"] is True
    assert contextual["original_capture_id"] == "original-v1"
    try:
        compare(original, reconstructed, context,
                {"schema_version": 1, "id": "reconstructed-v1", "objective": "other",
                 "stimulus": context["stimulus"]})
    except ValueError as error:
        assert "objectives differ" in str(error)
    else:
        raise AssertionError("incompatible capture contexts were accepted")
    assert context_errors(context, {"schema_version": 1, "id": "other", "objective": "other", "stimulus": context["stimulus"]}) == ["capture objectives differ"]
    malformed_context_errors = context_errors([], {})
    assert "original capture manifest must be an object" in malformed_context_errors
    assert "reconstructed capture manifest schema_version must be 1" in malformed_context_errors
    provenance_errors = capture_provenance_errors({}, Path("events.ndjson"), Path.cwd(), "original")
    assert any("missing stable capture id" in error for error in provenance_errors)
    reconstructed[1]["value"] = 78
    result = compare(original, reconstructed)
    assert result["outcome"] == "divergence"
    assert result["matched_prefix_events"] == 1
    assert result["first_divergence_index"] == 1
    assert result["last_matching_event"]["name"] == "reset"
    assert result["first_divergence"]["original"]["name"] == "scheduler"
    assert result["original_checkpoints"] == ["reset", "scheduler"]
    truncated = compare(original, original[:1])
    assert truncated["first_divergence_index"] == 1
    assert truncated["reconstructed_event"] is None
    with tempfile.TemporaryDirectory() as directory:
        malformed = Path(directory) / "malformed.ndjson"
        malformed.write_text('{"seq": 0}\n', encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "event kind" in str(error)
        else:
            raise AssertionError("malformed event was accepted")
        malformed.write_text('{"kind": "checkpoint", "seq": -1}\n', encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "event seq" in str(error)
        else:
            raise AssertionError("negative sequence was accepted")
        malformed.write_text(
            '{"kind": "checkpoint", "seq": 1}\n{"kind": "checkpoint", "seq": 1}\n',
            encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "increase strictly" in str(error)
        else:
            raise AssertionError("duplicate sequence was accepted")
    print("PASS: ordered event comparison identifies the first divergence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
