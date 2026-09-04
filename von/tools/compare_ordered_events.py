#!/usr/bin/env python3
"""Compare bounded original/reconstructed NDJSON event streams."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VOLATILE_FIELDS = {"seq", "time", "frame", "source_line"}


def load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    previous_sequence: int | None = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(event, dict):
            raise ValueError(f"{path}:{line_number}: event must be an object")
        if not isinstance(event.get("kind"), str) or not event["kind"]:
            raise ValueError(f"{path}:{line_number}: event kind must be a non-empty string")
        sequence = event.get("seq")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
            raise ValueError(f"{path}:{line_number}: event seq must be a non-negative integer")
        if previous_sequence is not None and sequence <= previous_sequence:
            raise ValueError(f"{path}:{line_number}: event seq must increase strictly")
        previous_sequence = sequence
        events.append(event)
    return events


def validate_order(events: list[dict[str, Any]]) -> None:
    previous_sequence: int | None = None
    for index, event in enumerate(events):
        if not isinstance(event, dict) or not isinstance(event.get("kind"), str) or not event["kind"]:
            raise ValueError(f"event {index}: kind must be a non-empty string")
        sequence = event.get("seq")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
            raise ValueError(f"event {index}: seq must be a non-negative integer")
        if previous_sequence is not None and sequence <= previous_sequence:
            raise ValueError(f"event {index}: seq must increase strictly")
        previous_sequence = sequence


def comparable(event: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in event.items() if key not in VOLATILE_FIELDS}


def checkpoints(events: list[dict[str, Any]]) -> list[str]:
    result = []
    for event in events:
        if event.get("kind") != "checkpoint":
            continue
        name = event.get("name", event.get("checkpoint"))
        if isinstance(name, str) and name not in result:
            result.append(name)
    return result


def context_errors(original: dict[str, Any], reconstructed: dict[str, Any]) -> list[str]:
    errors = []
    for label, context in (("original", original), ("reconstructed", reconstructed)):
        if not isinstance(context, dict):
            errors.append(f"{label} capture manifest must be an object")
            continue
        if context.get("schema_version") != 1:
            errors.append(f"{label} capture manifest schema_version must be 1")
        if not isinstance(context.get("id"), str) or not context["id"]:
            errors.append(f"{label} capture manifest requires id")
    if not isinstance(original, dict) or not isinstance(reconstructed, dict):
        return errors
    if original.get("objective") != reconstructed.get("objective"):
        errors.append("capture objectives differ")
    if original.get("stimulus") != reconstructed.get("stimulus"):
        errors.append("capture stimuli differ")
    return errors


def compare(original: list[dict[str, Any]], reconstructed: list[dict[str, Any]],
            original_context: dict[str, Any] | None = None,
            reconstructed_context: dict[str, Any] | None = None) -> dict[str, Any]:
    validate_order(original)
    validate_order(reconstructed)
    common = min(len(original), len(reconstructed))
    divergence = next(
        (index for index in range(common)
         if comparable(original[index]) != comparable(reconstructed[index])),
        common if len(original) != len(reconstructed) else None,
    )
    result: dict[str, Any] = {
        "schema_version": 1,
        "compared_events": common,
        "original_events": len(original),
        "reconstructed_events": len(reconstructed),
        "matched_prefix_events": divergence if divergence is not None else common,
        "outcome": "pass" if divergence is None else "divergence",
        "original_checkpoints": checkpoints(original),
        "reconstructed_checkpoints": checkpoints(reconstructed),
    }
    if original_context is not None and reconstructed_context is not None:
        result["original_capture_id"] = original_context.get("id")
        result["reconstructed_capture_id"] = reconstructed_context.get("id")
        result["context_compatible"] = not context_errors(original_context, reconstructed_context)
    result["missed_checkpoints"] = [
        name for name in result["original_checkpoints"]
        if name not in result["reconstructed_checkpoints"]
    ]
    result["unexpected_checkpoints"] = [
        name for name in result["reconstructed_checkpoints"]
        if name not in result["original_checkpoints"]
    ]
    result["last_matching_event"] = original[divergence - 1] if divergence and divergence > 0 else None
    if divergence is not None:
        result["first_divergence_index"] = divergence
        result["original_event"] = original[divergence] if divergence < len(original) else None
        result["reconstructed_event"] = reconstructed[divergence] if divergence < len(reconstructed) else None
        result["first_divergence"] = {
            "original": result["original_event"],
            "reconstructed": result["reconstructed_event"],
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("reconstructed", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--original-manifest", type=Path)
    parser.add_argument("--reconstructed-manifest", type=Path)
    args = parser.parse_args()
    try:
        original_context = json.loads(args.original_manifest.read_text(encoding="utf-8")) if args.original_manifest else None
        reconstructed_context = json.loads(args.reconstructed_manifest.read_text(encoding="utf-8")) if args.reconstructed_manifest else None
        if (original_context is None) != (reconstructed_context is None):
            raise ValueError("both capture manifests are required for provenance comparison")
        if original_context is not None:
            errors = context_errors(original_context, reconstructed_context)
            if errors:
                raise ValueError("; ".join(errors))
        result = compare(load_events(args.original), load_events(args.reconstructed), original_context, reconstructed_context)
    except ValueError as error:
        print(f"event comparison: {error}", file=sys.stderr)
        return 2
    encoded = json.dumps(result, indent=2)
    if args.summary:
        args.summary.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if result["outcome"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
