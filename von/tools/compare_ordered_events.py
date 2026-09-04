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
        validate_event_shape(event, f"{path}:{line_number}")
        previous_sequence = sequence
        events.append(event)
    return events


def validate_event_shape(event: dict[str, Any], where: str) -> None:
    required_fields = {
        "direct-call": ("pc", "target"),
        "indirect-call": ("pc", "target"),
        "return": ("pc", "next_pc"),
        "exception": ("pc",),
        "reset": ("pc",),
        "checkpoint": ("name",),
    }.get(event["kind"], ())
    for field in required_fields:
        if field not in event or event[field] is None or event[field] == "":
            raise ValueError(f"{where}: {event['kind']} requires {field}")


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
        validate_event_shape(event, f"event {index}")
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


def dynamic_edges(events: list[dict[str, Any]]) -> set[tuple[str, str]]:
    """Extract edges only from ordered call events, never from PC-set coverage."""
    edges: set[tuple[str, str]] = set()
    for event in events:
        if event.get("kind") not in {"direct-call", "indirect-call"}:
            continue
        caller, target = event.get("pc"), event.get("target")
        if caller is not None and target is not None:
            edges.add((str(caller), str(target)))
    return edges


def indirect_targets(events: list[dict[str, Any]]) -> set[str]:
    return {str(event["target"]) for event in events
            if event.get("kind") == "indirect-call" and event.get("target") is not None}


def edge_records(edges: set[tuple[str, str]]) -> list[list[str]]:
    """Encode dynamic edge sets deterministically for JSON reports."""
    return [[caller, target] for caller, target in sorted(edges)]


def provenance_summary(context: dict[str, Any]) -> dict[str, Any]:
    """Keep comparison provenance compact and free of command/path details."""
    return {
        "id": context.get("id"),
        "objective": context.get("objective"),
        "stimulus": context.get("stimulus"),
        "checkpoints": context.get("checkpoints"),
        "hypothesis": context.get("hypothesis"),
        "expected_discriminator": context.get("expected_discriminator"),
    }


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
    original_configuration = original.get("configuration")
    reconstructed_configuration = reconstructed.get("configuration")
    if not isinstance(original_configuration, dict):
        errors.append("original capture configuration must be an object")
    if not isinstance(reconstructed_configuration, dict):
        errors.append("reconstructed capture configuration must be an object")
    if isinstance(original_configuration, dict) and isinstance(reconstructed_configuration, dict):
        for field in ("set", "mame_revision", "execution_engine"):
            if original_configuration.get(field) != reconstructed_configuration.get(field):
                errors.append(f"capture configuration.{field} differs")
    original_inputs = original.get("inputs")
    reconstructed_inputs = reconstructed.get("inputs")
    if original_inputs is not None or reconstructed_inputs is not None:
        if not isinstance(original_inputs, list) or not isinstance(reconstructed_inputs, list):
            errors.append("capture input inventories must be arrays")
        else:
            def input_hashes(items: list[Any]) -> list[str]:
                return sorted(item.get("sha256", "") for item in items
                              if isinstance(item, dict))
            if input_hashes(original_inputs) != input_hashes(reconstructed_inputs):
                errors.append("capture input inventories differ")
    return errors


def capture_provenance_errors(context: Any, event_path: Path, root: Path,
                              label: str) -> list[str]:
    """Require a CLI comparison context to be a valid sidecar for its stream."""
    errors: list[str] = []
    if not isinstance(context, dict):
        return [f"{label} capture manifest must be an object"]
    try:
        from capture_manifest import validate as validate_capture

        errors.extend(f"{label} capture: {error}" for error in validate_capture(context, root))
    except (ImportError, TypeError) as error:
        errors.append(f"{label} capture validation failed: {error}")
    try:
        relative_event = str(event_path.resolve().relative_to(root.resolve()))
    except ValueError:
        errors.append(f"{label} event stream escapes capture root")
        return errors
    artifacts = context.get("artifacts", [])
    artifact_paths = {
        item.get("path") for item in artifacts
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    } if isinstance(artifacts, list) else set()
    if relative_event not in artifact_paths:
        errors.append(f"{label} event stream is not a declared capture artifact: {relative_event}")
    return errors


def compare(original: list[dict[str, Any]], reconstructed: list[dict[str, Any]],
            original_context: dict[str, Any] | None = None,
            reconstructed_context: dict[str, Any] | None = None) -> dict[str, Any]:
    if (original_context is None) != (reconstructed_context is None):
        raise ValueError("both capture contexts are required for provenance comparison")
    if original_context is not None and reconstructed_context is not None:
        context_problems = context_errors(original_context, reconstructed_context)
        if context_problems:
            raise ValueError("; ".join(context_problems))
    validate_order(original)
    validate_order(reconstructed)
    original_edges = dynamic_edges(original)
    reconstructed_edges = dynamic_edges(reconstructed)
    original_indirect = indirect_targets(original)
    reconstructed_indirect = indirect_targets(reconstructed)
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
        "confirmed_dynamic_edge_count": len(original_edges),
        "observed_indirect_targets": sorted(original_indirect),
        "observed_indirect_target_count": len(original_indirect),
        "original_dynamic_edges": edge_records(original_edges),
        "reconstructed_dynamic_edges": edge_records(reconstructed_edges),
        "missing_dynamic_edges": edge_records(original_edges - reconstructed_edges),
        "unexpected_dynamic_edges": edge_records(reconstructed_edges - original_edges),
        "missing_indirect_targets": sorted(original_indirect - reconstructed_indirect),
        "unexpected_indirect_targets": sorted(reconstructed_indirect - original_indirect),
    }
    if original_context is not None and reconstructed_context is not None:
        result["original_capture_id"] = original_context.get("id")
        result["reconstructed_capture_id"] = reconstructed_context.get("id")
        result["context_compatible"] = not context_errors(original_context, reconstructed_context)
        result["capture_provenance"] = {
            "original": provenance_summary(original_context),
            "reconstructed": provenance_summary(reconstructed_context),
        }
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
    parser.add_argument("--capture-root", type=Path, default=Path.cwd(),
                        help="root used to validate capture manifests and artifact paths")
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
            provenance_errors = capture_provenance_errors(
                original_context, args.original, args.capture_root, "original")
            provenance_errors.extend(capture_provenance_errors(
                reconstructed_context, args.reconstructed, args.capture_root, "reconstructed"))
            if provenance_errors:
                raise ValueError("; ".join(provenance_errors))
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
