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
    altered_calls = copy.deepcopy(calls)
    altered_calls[-2]["target"] = "0x30"
    altered_calls[-1]["target"] = "0x30"
    edge_delta = compare(calls, altered_calls)
    assert edge_delta["missing_dynamic_edges"] == [["0x10", "0x20"]]
    assert edge_delta["unexpected_dynamic_edges"] == [["0x10", "0x30"]]
    assert edge_delta["missing_indirect_targets"] == ["0x20"]
    assert edge_delta["unexpected_indirect_targets"] == ["0x30"]
    assert compare(original, reconstructed)["missed_checkpoints"] == []
    configuration = {"set": "vonj", "mame_revision": "abc", "execution_engine": "interpreter",
                    "patch_profile": "original"}
    context = {"schema_version": 1, "id": "original-v1", "objective": "pilot",
               "stimulus": {"kind": "attract", "seconds": 1}, "configuration": configuration,
               "checkpoints": ["reset", "scheduler"],
               "hypothesis": "startup reaches scheduler",
               "expected_discriminator": "scheduler checkpoint"}
    reconstructed_context = {"schema_version": 1, "id": "reconstructed-v1", "objective": "pilot",
                             "stimulus": {"kind": "attract", "seconds": 1},
                             "configuration": {**configuration, "patch_profile": "reconstructed"},
                             "checkpoints": ["reset", "scheduler"],
                             "hypothesis": "startup reaches scheduler",
                             "expected_discriminator": "scheduler checkpoint"}
    contextual = compare(original, reconstructed, context, reconstructed_context)
    assert contextual["context_compatible"] is True
    assert contextual["original_capture_id"] == "original-v1"
    assert contextual["capture_provenance"]["original"]["checkpoints"] == ["reset", "scheduler"]
    assert contextual["capture_provenance"]["original"]["hypothesis"] == "startup reaches scheduler"
    checkpoint_missing = compare(original[:1], original[:1], context, reconstructed_context)
    assert checkpoint_missing["outcome"] == "divergence"
    assert checkpoint_missing["checkpoint_outcome"] == "divergence"
    assert checkpoint_missing["missing_original_checkpoints"] == ["scheduler"]
    assert checkpoint_missing["missing_reconstructed_checkpoints"] == ["scheduler"]
    context["inputs"] = [{"path": "original-rom.json", "sha256": "a" * 64}]
    reconstructed_context["inputs"] = [{"path": "isolated-rom.json", "sha256": "a" * 64}]
    assert compare(original, reconstructed, context, reconstructed_context)["outcome"] == "pass"
    mismatched_inputs = copy.deepcopy(reconstructed_context)
    mismatched_inputs["inputs"][0]["sha256"] = "b" * 64
    assert any("input inventories differ" in error
               for error in context_errors(context, mismatched_inputs))
    mismatched_checkpoints = copy.deepcopy(reconstructed_context)
    mismatched_checkpoints["checkpoints"] = ["reset"]
    assert any("capture checkpoints differ" in error
               for error in context_errors(context, mismatched_checkpoints))
    try:
        compare(original, reconstructed, context,
                {"schema_version": 1, "id": "reconstructed-v1", "objective": "other",
                 "stimulus": context["stimulus"], "configuration": reconstructed_context["configuration"]})
    except ValueError as error:
        assert "objectives differ" in str(error)
    else:
        raise AssertionError("incompatible capture contexts were accepted")
    assert context_errors(context, {"schema_version": 1, "id": "other", "objective": "other",
                                    "stimulus": context["stimulus"],
                                    "configuration": reconstructed_context["configuration"],
                                    "inputs": reconstructed_context["inputs"],
                                    "checkpoints": reconstructed_context["checkpoints"]}) == ["capture objectives differ"]
    mismatched_configuration = copy.deepcopy(reconstructed_context)
    mismatched_configuration["configuration"]["mame_revision"] = "def"
    assert any("configuration.mame_revision differs" in error
               for error in context_errors(context, mismatched_configuration))
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
            '{"kind": "checkpoint", "name": "x", "seq": 1}\n'
            '{"kind": "checkpoint", "name": "x", "seq": 1}\n',
            encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "increase strictly" in str(error)
        else:
            raise AssertionError("duplicate sequence was accepted")
        malformed.write_text('{"kind": "indirect-call", "seq": 1}\n', encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "indirect-call requires pc" in str(error)
        else:
            raise AssertionError("incomplete indirect-call event was accepted")
    print("PASS: ordered event comparison identifies the first divergence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
