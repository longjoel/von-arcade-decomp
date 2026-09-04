#!/usr/bin/env python3
"""Contract tests for ordered causal event comparison."""

from __future__ import annotations

import copy
import gzip
import hashlib
import tempfile
from pathlib import Path

from compare_ordered_events import (capture_provenance_errors, compare, context_errors,
                                    event_artifact_provenance, load_events)


def main() -> int:
    fixture_root = Path(__file__).resolve().parents[1] / "tests/fixtures/ordered-events"
    fixture_report = compare(
        load_events(fixture_root / "original.ndjson"),
        load_events(fixture_root / "reconstructed.ndjson"),
    )
    assert fixture_report["first_divergence_index"] == 2
    assert fixture_report["last_matching_event"]["name"] == "scheduler"
    assert fixture_report["first_divergence"]["original"]["target"] == "0x00002000"
    assert fixture_report["first_divergence"]["reconstructed"]["target"] == "0x00003000"
    original = [
        {"seq": 1, "time": 1.0, "frame": 1, "cpu": "maincpu", "kind": "checkpoint", "name": "reset"},
        {"seq": 2, "time": 1.0, "frame": 1, "cpu": "maincpu", "kind": "checkpoint", "name": "scheduler"},
        {"seq": 3, "time": 1.1, "frame": 2, "cpu": "maincpu", "kind": "mmio-write", "address": "0x4d", "value": 77},
    ]
    reconstructed = copy.deepcopy(original)
    reconstructed[0]["seq"] = 100
    reconstructed[1]["seq"] = 101
    reconstructed[2]["seq"] = 102
    reconstructed[0]["time"] = 9.0
    reconstructed[0]["source_line"] = 900
    assert compare(original, reconstructed)["outcome"] == "pass"
    calls = original + [
        {"seq": 4, "time": 1.2, "frame": 2, "cpu": "maincpu", "kind": "indirect-call",
         "pc": "0x10", "next_pc": "0x20", "target": "0x20"},
        {"seq": 5, "time": 1.3, "frame": 2, "cpu": "maincpu", "kind": "indirect-call",
         "pc": "0x10", "next_pc": "0x20", "target": "0x20"},
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
            '{"kind": "checkpoint", "name": "x", "time": 1.0, "frame": 1, "cpu": "maincpu", "seq": 1}\n'
            '{"kind": "checkpoint", "name": "x", "time": 1.0, "frame": 1, "cpu": "maincpu", "seq": 1}\n',
            encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "increase strictly" in str(error)
        else:
            raise AssertionError("duplicate sequence was accepted")
        malformed.write_text(
            '{"kind": "indirect-call", "seq": 1, "time": 1.0, "frame": 1, "cpu": "maincpu"}\n',
            encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "indirect-call requires pc" in str(error)
        else:
            raise AssertionError("incomplete indirect-call event was accepted")
        malformed.write_text(
            '{"kind": "checkpoint", "seq": 1, "time": "1.0", "frame": 1, '
            '"cpu": "maincpu", "name": "x"}\n', encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "time must be a finite non-negative number" in str(error)
        else:
            raise AssertionError("non-numeric checkpoint time was accepted")
        malformed.write_text(
            '{"kind": "checkpoint", "seq": 1, "time": 1.0, "frame": true, '
            '"cpu": "maincpu", "name": "x"}\n', encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "frame must be a non-negative integer" in str(error)
        else:
            raise AssertionError("boolean checkpoint frame was accepted")
        malformed.write_text(
            '{"kind": "mmio-write", "seq": 1, "time": 1.0, "frame": 1, '
            '"cpu": "maincpu", "address": "0x4d"}\n', encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "mmio-write requires value" in str(error)
        else:
            raise AssertionError("incomplete MMIO event was accepted")
        malformed.write_text(
            '{"kind": "direct-call", "seq": 1, "time": 1.0, "frame": 1, '
            '"cpu": "maincpu", "pc": {}, "next_pc": "0x20", "target": "0x20"}\n',
            encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "direct-call pc must be a scalar address" in str(error)
        else:
            raise AssertionError("non-scalar PC was accepted")
        malformed.write_text(
            '{"kind": "checkpoint", "seq": 1, "time": 1.0, "frame": 1, '
            '"cpu": "maincpu", "name": {}}\n', encoding="utf-8")
        try:
            load_events(malformed)
        except ValueError as error:
            assert "checkpoint name must be a non-empty string" in str(error)
        else:
            raise AssertionError("non-string checkpoint name was accepted")
        compressed_original = Path(directory) / "original.ndjson.gz"
        compressed_reconstructed = Path(directory) / "reconstructed.ndjson.gz"
        payload = ('{"seq": 1, "time": 1.0, "frame": 1, "cpu": "maincpu", '
                   '"kind": "checkpoint", "name": "reset"}\n').encode()
        for compressed in (compressed_original, compressed_reconstructed):
            with gzip.open(compressed, "wb") as stream:
                stream.write(payload)
        assert compare(load_events(compressed_original), load_events(compressed_reconstructed))["outcome"] == "pass"
        original_digest = hashlib.sha256(compressed_original.read_bytes()).hexdigest()
        provenance = event_artifact_provenance(
            {"artifacts": [{"path": "original.ndjson.gz", "sha256": original_digest}]},
            compressed_original, Path(directory))
        assert provenance == {"path": "original.ndjson.gz", "sha256": original_digest}
        try:
            event_artifact_provenance(
                {"artifacts": [{"path": "original.ndjson.gz", "sha256": "a" * 64}]},
                compressed_original, Path(directory))
        except ValueError as error:
            assert "artifact hash mismatch" in str(error)
        else:
            raise AssertionError("stale artifact hash was accepted")
        try:
            event_artifact_provenance({"artifacts": []}, compressed_original, Path(directory))
        except ValueError as error:
            assert "no hashed artifact declaration" in str(error)
        else:
            raise AssertionError("undeclared comparison provenance was accepted")
        compressed_original.write_bytes(b"not gzip")
        try:
            load_events(compressed_original)
        except ValueError as error:
            assert "unable to read event stream" in str(error)
        else:
            raise AssertionError("invalid gzip stream was accepted")
    print("PASS: ordered event comparison identifies the first divergence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
