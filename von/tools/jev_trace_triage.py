#!/usr/bin/env python3
"""Prepare and optionally submit bounded CPU-trace triage dossiers to JEV."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from compare_ordered_events import compare, load_events


SCHEMA_VERSION = 1
DEFAULT_STATE_BYTE_LIMIT = 80_000
DEFAULT_EVENT_RADIUS = 12
DEFAULT_DISASSEMBLY_RADIUS = 8
DEFAULT_CANDIDATES = 8

PROVIDERS = {
    "openrouter": {
        "endpoint": "https://openrouter.ai/api/alpha/decisions",
        "key": "OPENROUTER_API_KEY",
        "model": "typesafe/jev-1.13",
    },
    "typesafe": {
        "endpoint": "https://api.typesafe.ai/v1/systemone",
        "key": "TYPESAFE_API_KEY",
        "model": "jev-latest",
    },
}

CATEGORIES = {
    "control_flow": "Wrong, missing, or unexpected call, branch, return, or target.",
    "missing_initialization": "Required state was never initialized or was initialized incorrectly.",
    "state_update": "A RAM or logical state transition differs despite matching control flow.",
    "mmio_fifo_protocol": "A device register, command, FIFO, or handshake interaction differs.",
    "timing_order": "The relevant operations occur in the wrong frame, time, or order.",
    "data_decoding": "A packed field, table, pointer, numeric value, or data format is interpreted incorrectly.",
    "trace_artifact": "The apparent difference is caused by capture, normalization, or comparison artifacts.",
    "insufficient_evidence": "The supplied evidence does not distinguish a causal category.",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to read {label} {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return value


def manifest_summary(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    manifest = load_json_object(path, "capture manifest")
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "id": manifest.get("id"),
        "objective": manifest.get("objective"),
        "hypothesis": manifest.get("hypothesis"),
        "expected_discriminator": manifest.get("expected_discriminator"),
        "stimulus": manifest.get("stimulus"),
        "checkpoints": manifest.get("checkpoints"),
    }


def address(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return None
    try:
        return int(value, 0)
    except ValueError:
        try:
            return int(value, 16)
        except ValueError:
            return None


def format_address(value: int) -> str:
    return f"0x{value:08x}"


def candidate_addresses(comparison: dict[str, Any], original: list[dict[str, Any]],
                        reconstructed: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """Build a deterministic causal candidate list without model inference."""
    found: dict[int, dict[str, Any]] = {}

    def add(value: Any, reason: str, priority: int) -> None:
        parsed = address(value)
        if parsed is None:
            return
        candidate = found.setdefault(parsed, {
            "address": format_address(parsed), "priority": priority, "reasons": []
        })
        candidate["priority"] = min(candidate["priority"], priority)
        if reason not in candidate["reasons"]:
            candidate["reasons"].append(reason)

    divergence = comparison.get("first_divergence_index")
    if isinstance(divergence, int):
        for stream_name, events in (("original", original), ("reconstructed", reconstructed)):
            if divergence < len(events):
                event = events[divergence]
                for field, priority in (("pc", 0), ("target", 1), ("address", 1), ("next_pc", 2)):
                    add(event.get(field), f"{stream_name} divergence {field}", priority)
        if divergence > 0:
            for stream_name, events in (("original", original), ("reconstructed", reconstructed)):
                event = events[divergence - 1]
                for field in ("pc", "target", "address", "next_pc"):
                    add(event.get(field), f"last matching {stream_name} {field}", 3)
    for caller, target in comparison.get("missing_dynamic_edges", []):
        add(target, f"missing dynamic target called from {caller}", 2)
        add(caller, f"caller of missing dynamic target {target}", 3)
    for target in comparison.get("missing_indirect_targets", []):
        add(target, "missing indirect target", 2)
    ordered = sorted(found.values(), key=lambda item: (item["priority"], int(item["address"], 16)))
    for index, item in enumerate(ordered[:limit]):
        item["id"] = f"candidate_{index}"
    return ordered[:limit]


DISASSEMBLY_LINE = re.compile(r"^\s*([0-9a-fA-F]+):")


def disassembly_windows(path: Path | None, candidates: list[dict[str, Any]],
                        radius: int) -> dict[str, list[str]]:
    if path is None:
        return {}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as error:
        raise ValueError(f"unable to read disassembly {path}: {error}") from error
    wanted = {int(item["address"], 16): item["id"] for item in candidates}
    hits: dict[str, int] = {}
    nearest: dict[int, tuple[int, int]] = {target: (1 << 63, -1) for target in wanted}
    for index, line in enumerate(lines):
        match = DISASSEMBLY_LINE.match(line)
        if not match:
            continue
        current = int(match.group(1), 16)
        for target in wanted:
            distance = abs(current - target)
            if distance < nearest[target][0]:
                nearest[target] = (distance, index)
    for target, identifier in wanted.items():
        if nearest[target][1] >= 0:
            hits[identifier] = nearest[target][1]
    return {
        identifier: lines[max(0, index - radius):index + radius + 1]
        for identifier, index in sorted(hits.items())
    }


def annotation_matches(paths: list[Path], candidates: list[dict[str, Any]],
                       line_limit: int = 24) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for item in candidates:
        numeric = int(item["address"], 16)
        needles = {item["address"].lower(), f"0x{numeric:x}", f"{numeric:x}"}
        matches: list[str] = []
        for path in paths:
            try:
                for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                    lowered = line.lower()
                    if any(needle in lowered for needle in needles):
                        matches.append(f"{path.name}: {line.strip()}")
                        if len(matches) >= line_limit:
                            break
            except OSError as error:
                raise ValueError(f"unable to read annotation {path}: {error}") from error
            if len(matches) >= line_limit:
                break
        if matches:
            result[item["id"]] = matches
    return result


def ledger_matches(path: Path | None, candidates: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    if path is None:
        return {}
    ledger = load_json_object(path, "reconstruction ledger")
    result: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        target = int(candidate["address"], 16)
        matches = []
        for image in ledger.get("images", []):
            if not isinstance(image, dict):
                continue
            for unit in image.get("work_units", []):
                if not isinstance(unit, dict):
                    continue
                for item_range in unit.get("ranges", []):
                    if not isinstance(item_range, dict):
                        continue
                    start, end = address(item_range.get("start")), address(item_range.get("end"))
                    if start is not None and end is not None and start <= target < end:
                        matches.append({
                            "image": image.get("name"), "id": unit.get("id"),
                            "name": unit.get("name"), "stage": unit.get("stage"),
                            "dependencies": unit.get("dependencies", []),
                            "range": item_range,
                        })
                        break
        if matches:
            result[candidate["id"]] = matches
    return result


def event_window(events: list[dict[str, Any]], divergence: int, radius: int) -> list[dict[str, Any]]:
    return events[max(0, divergence - radius):min(len(events), divergence + radius + 1)]


def compact_comparison(comparison: dict[str, Any], edge_limit: int = 32) -> dict[str, Any]:
    """Retain causal summary fields without embedding whole-run edge inventories."""
    scalar_fields = (
        "outcome", "compared_events", "original_events", "reconstructed_events",
        "matched_prefix_events", "first_divergence_index", "checkpoint_outcome",
        "checkpoint_order_match", "original_checkpoints", "reconstructed_checkpoints",
        "missed_checkpoints", "unexpected_checkpoints", "missing_original_checkpoints",
        "missing_reconstructed_checkpoints", "last_matching_event", "first_divergence",
    )
    result = {field: comparison.get(field) for field in scalar_fields if field in comparison}
    for field in ("missing_dynamic_edges", "unexpected_dynamic_edges",
                  "missing_indirect_targets", "unexpected_indirect_targets"):
        values = comparison.get(field, [])
        result[field] = values[:edge_limit] if isinstance(values, list) else []
        result[f"{field}_total"] = len(values) if isinstance(values, list) else 0
    return result


def build_dossier(original_path: Path, reconstructed_path: Path, *,
                  original_manifest: Path | None = None,
                  reconstructed_manifest: Path | None = None,
                  disassembly: Path | None = None, annotations: list[Path] | None = None,
                  ledger: Path | None = None, event_radius: int = DEFAULT_EVENT_RADIUS,
                  disassembly_radius: int = DEFAULT_DISASSEMBLY_RADIUS,
                  candidate_limit: int = DEFAULT_CANDIDATES,
                  state_byte_limit: int = DEFAULT_STATE_BYTE_LIMIT) -> dict[str, Any]:
    if event_radius < 0 or disassembly_radius < 0 or candidate_limit < 1 or state_byte_limit < 1:
        raise ValueError("window radii must be non-negative and limits must be positive")
    original = load_events(original_path)
    reconstructed = load_events(reconstructed_path)
    comparison = compare(original, reconstructed)
    if comparison["outcome"] != "divergence":
        raise ValueError("event streams do not diverge; there is nothing for JEV to triage")
    divergence = comparison["first_divergence_index"]
    candidates = candidate_addresses(comparison, original, reconstructed, candidate_limit)
    if not candidates:
        raise ValueError("the first divergence contains no address-like causal candidates")
    original_manifest_summary = manifest_summary(original_manifest)
    reconstructed_manifest_summary = manifest_summary(reconstructed_manifest)
    if original_manifest_summary is not None and reconstructed_manifest_summary is not None:
        for field in ("objective", "stimulus", "checkpoints"):
            if original_manifest_summary.get(field) != reconstructed_manifest_summary.get(field):
                raise ValueError(f"capture manifests have different {field}")
    dossier = {
        "schema_version": SCHEMA_VERSION,
        "purpose": "advisory CPU trace divergence triage; never validation evidence",
        "sources": {
            "original": {"path": str(original_path), "sha256": sha256_file(original_path),
                         "manifest": original_manifest_summary},
            "reconstructed": {"path": str(reconstructed_path),
                               "sha256": sha256_file(reconstructed_path),
                               "manifest": reconstructed_manifest_summary},
            "disassembly": ({"path": str(disassembly), "sha256": sha256_file(disassembly)}
                            if disassembly else None),
            "annotations": [{"path": str(path), "sha256": sha256_file(path)}
                            for path in annotations or []],
            "ledger": ({"path": str(ledger), "sha256": sha256_file(ledger)} if ledger else None),
        },
        "comparison": compact_comparison(comparison),
        "windows": {
            "original": event_window(original, divergence, event_radius),
            "reconstructed": event_window(reconstructed, divergence, event_radius),
        },
        "candidates": candidates,
        "disassembly": disassembly_windows(disassembly, candidates, disassembly_radius),
        "annotations": annotation_matches(annotations or [], candidates),
        "ledger_matches": ledger_matches(ledger, candidates),
        "bounds": {
            "event_radius": event_radius, "disassembly_radius": disassembly_radius,
            "candidate_limit": candidate_limit, "state_byte_limit": state_byte_limit,
        },
    }
    dossier["bounds"]["state_bytes"] = 0
    for _ in range(4):
        size = len(canonical_bytes(dossier))
        if dossier["bounds"]["state_bytes"] == size:
            break
        dossier["bounds"]["state_bytes"] = size
    size = len(canonical_bytes(dossier))
    if size > state_byte_limit:
        raise ValueError(
            f"dossier is {size} bytes, exceeding --max-state-bytes {state_byte_limit}; "
            "reduce event or disassembly windows"
        )
    return dossier


def build_request(dossier: dict[str, Any], model: str) -> dict[str, Any]:
    questions: dict[str, Any] = {
        "divergence_category": {
            "type": "choice",
            "instructions": "Classify the most likely immediate cause of the first trace divergence. Use only supplied evidence.",
            "criteria": CATEGORIES,
        },
        "causal_proximity": {
            "type": "score",
            "instructions": "Rate how closely the strongest supplied candidate is tied to the first observable divergence.",
            "criteria": [
                "Only static or coincidental proximity",
                "Weak indirect relationship",
                "Plausible dependency on the dynamic path",
                "Direct producer or caller near the divergence",
                "Observed instruction or target at the divergence",
            ],
        },
        "evidence_sufficient": {
            "type": "noul",
            "instructions": "Is this bounded dossier sufficient to rank at least one supplied candidate above the others?",
            "criteria": {"true": "Evidence distinguishes at least one candidate",
                         "false": "Candidates remain indistinguishable or evidence is missing"},
        },
    }
    for candidate in dossier["candidates"]:
        questions[f"supports_{candidate['id']}"] = {
            "type": "noul",
            "instructions": (
                f"Does the evidence support {candidate['id']} at {candidate['address']} "
                "as a cause or direct producer of the first divergence?"
            ),
            "criteria": {"true": "Causally supported by ordered dynamic evidence",
                         "false": "Merely nearby, downstream, contradicted, or unsupported"},
        }
    return {"model": model, "state": dossier, "questions": questions}


def parse_env_file(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise ValueError(f"unable to read env file {path}: {error}") from error
    values: dict[str, str] = {}
    for line_number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ValueError(f"{path}:{line_number}: expected NAME=VALUE")
        name, value = line.split("=", 1)
        name, value = name.strip(), value.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError(f"{path}:{line_number}: invalid variable name")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[name] = value
    return values


def provider_settings(provider: str, model: str | None, env_file: Path | None) -> tuple[str, str, str]:
    settings = PROVIDERS[provider]
    values = parse_env_file(env_file) if env_file else {}
    key_name = settings["key"]
    api_key = os.environ.get(key_name) or values.get(key_name)
    if not api_key:
        location = f" or {env_file}" if env_file else ""
        raise ValueError(f"missing {key_name} in the environment{location}")
    return settings["endpoint"], model or settings["model"], api_key


def post_json(endpoint: str, api_key: str, payload: dict[str, Any], *, timeout: float = 30.0,
              attempts: int = 3, opener: Callable[..., Any] = urllib.request.urlopen,
              sleeper: Callable[[float], None] = time.sleep) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    body = canonical_bytes(payload)
    retries: list[dict[str, Any]] = []
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(
            endpoint, data=body, method="POST",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
                     "User-Agent": "von-arcade-decomp/jev-triage"},
        )
        try:
            with opener(request, timeout=timeout) as response:
                decoded = json.loads(response.read().decode("utf-8"))
            if not isinstance(decoded, dict):
                raise ValueError("JEV response must be a JSON object")
            return decoded, retries
        except urllib.error.HTTPError as error:
            if error.code not in {429, 529} or attempt == attempts:
                raise ValueError(f"JEV request failed with HTTP {error.code}") from error
            retries.append({"attempt": attempt, "status": error.code})
        except urllib.error.URLError as error:
            if attempt == attempts:
                raise ValueError(f"JEV request failed: {error.reason}") from error
            retries.append({"attempt": attempt, "error": type(error.reason).__name__})
        delay = min(2 ** (attempt - 1), 4)
        sleeper(delay)
    raise AssertionError("unreachable")


def answer_payload(response: dict[str, Any]) -> tuple[dict[str, Any], str | None, dict[str, Any] | None]:
    envelope = response.get("data", response)
    if not isinstance(envelope, dict) or not isinstance(envelope.get("answers"), dict):
        raise ValueError("JEV response is missing an answers object")
    return envelope["answers"], envelope.get("model"), envelope.get("usage")


def noul_value(answers: dict[str, Any], key: str) -> float:
    answer = answers.get(key)
    if not isinstance(answer, dict) or answer.get("type") != "noul":
        raise ValueError(f"JEV response is missing noul answer {key}")
    value = answer.get("noul")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise ValueError(f"JEV noul answer {key} must be between 0 and 1")
    return float(value)


def make_report(dossier: dict[str, Any], request: dict[str, Any], response: dict[str, Any],
                provider: str, retries: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    answers, returned_model, usage = answer_payload(response)
    sufficient = noul_value(answers, "evidence_sufficient")
    ranked = []
    for candidate in dossier["candidates"]:
        ranked.append({**candidate, "support": noul_value(answers, f"supports_{candidate['id']}")})
    ranked.sort(key=lambda item: (-item["support"], item["priority"], item["address"]))
    top = ranked[0]["support"]
    second = ranked[1]["support"] if len(ranked) > 1 else 0.0
    reasons = []
    if sufficient < 0.5:
        reasons.append("JEV judged the evidence insufficient")
    if top < 0.55:
        reasons.append("no candidate reached 0.55 support")
    if len(ranked) > 1 and top - second < 0.10:
        reasons.append("top candidates are separated by less than 0.10")
    category = answers.get("divergence_category")
    causal = answers.get("causal_proximity")
    if not isinstance(category, dict) or category.get("type") != "choice":
        raise ValueError("JEV response is missing choice answer divergence_category")
    if not isinstance(causal, dict) or causal.get("type") != "score":
        raise ValueError("JEV response is missing score answer causal_proximity")
    return {
        "schema_version": SCHEMA_VERSION,
        "classification": "advisory-discovery-only",
        "provider": provider,
        "requested_model": request["model"],
        "returned_model": returned_model,
        "request_sha256": hashlib.sha256(canonical_bytes(request)).hexdigest(),
        "response_sha256": hashlib.sha256(canonical_bytes(response)).hexdigest(),
        "source_hashes": {
            key: value.get("sha256") if isinstance(value, dict) else None
            for key, value in dossier["sources"].items() if key != "annotations"
        },
        "usage": usage,
        "retries": retries or [],
        "evidence_sufficient": sufficient,
        "divergence_category": category,
        "causal_proximity": causal,
        "ranked_candidates": ranked,
        "abstained": bool(reasons),
        "abstention_reasons": reasons,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true", help="build a dossier without network access")
    mode.add_argument("--submit", action="store_true", help="build and submit a dossier")
    mode.add_argument("--replay", type=Path, metavar="RESPONSE", help="replay a saved JEV response")
    parser.add_argument("--original", type=Path)
    parser.add_argument("--reconstructed", type=Path)
    parser.add_argument("--original-manifest", type=Path)
    parser.add_argument("--reconstructed-manifest", type=Path)
    parser.add_argument("--disassembly", type=Path)
    parser.add_argument("--annotation", type=Path, action="append", default=[])
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--dossier", type=Path, help="prepared dossier to use with --replay")
    parser.add_argument("--output-dir", type=Path, default=Path("von/build/jev-triage"))
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="openrouter")
    parser.add_argument("--model")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--event-radius", type=int, default=DEFAULT_EVENT_RADIUS)
    parser.add_argument("--disassembly-radius", type=int, default=DEFAULT_DISASSEMBLY_RADIUS)
    parser.add_argument("--candidate-limit", type=int, default=DEFAULT_CANDIDATES)
    parser.add_argument("--max-state-bytes", type=int, default=DEFAULT_STATE_BYTE_LIMIT)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args(argv)
    if args.replay:
        if not args.dossier:
            parser.error("--replay requires --dossier")
    elif not args.original or not args.reconstructed:
        parser.error("--prepare and --submit require --original and --reconstructed")
    if (args.original_manifest is None) != (args.reconstructed_manifest is None):
        parser.error("capture manifests must be supplied together")
    if args.timeout <= 0 or args.attempts < 1:
        parser.error("--timeout and --attempts must be positive")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.replay:
            dossier = load_json_object(args.dossier, "dossier")
            response = load_json_object(args.replay, "JEV response")
            model = args.model or PROVIDERS[args.provider]["model"]
            request = build_request(dossier, model)
            report = make_report(dossier, request, response, args.provider)
            write_json(args.output_dir / "report.json", report)
            print(f"Wrote {args.output_dir / 'report.json'}")
            return 0

        dossier = build_dossier(
            args.original, args.reconstructed,
            original_manifest=args.original_manifest,
            reconstructed_manifest=args.reconstructed_manifest,
            disassembly=args.disassembly, annotations=args.annotation, ledger=args.ledger,
            event_radius=args.event_radius, disassembly_radius=args.disassembly_radius,
            candidate_limit=args.candidate_limit, state_byte_limit=args.max_state_bytes,
        )
        model = args.model or PROVIDERS[args.provider]["model"]
        request = build_request(dossier, model)
        write_json(args.output_dir / "dossier.json", dossier)
        write_json(args.output_dir / "request.json", request)
        if args.prepare:
            print(f"Wrote {args.output_dir / 'dossier.json'}")
            print(f"Wrote {args.output_dir / 'request.json'}")
            return 0
        endpoint, model, api_key = provider_settings(args.provider, args.model, args.env_file)
        request["model"] = model
        write_json(args.output_dir / "request.json", request)
        response, retries = post_json(endpoint, api_key, request, timeout=args.timeout,
                                      attempts=args.attempts)
        report = make_report(dossier, request, response, args.provider, retries)
        write_json(args.output_dir / "response.json", response)
        write_json(args.output_dir / "report.json", report)
        print(f"Wrote {args.output_dir / 'report.json'}")
        if report["abstained"]:
            print("JEV abstained: " + "; ".join(report["abstention_reasons"]))
        else:
            best = report["ranked_candidates"][0]
            print(f"Advisory top candidate: {best['address']} (support={best['support']:.3f})")
        return 0
    except (OSError, ValueError) as error:
        print(f"jev trace triage: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
