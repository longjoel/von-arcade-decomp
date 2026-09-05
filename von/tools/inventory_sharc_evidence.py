#!/usr/bin/env python3
"""Inventory SHARC source artifacts and generated trace evidence.

The inventory is deliberately non-destructive.  Raw MAME output remains below
``von/build`` (or at the repository root for older probes); this tool gives the
large generated corpus one compact, reproducible index.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re

import reconstruction_progress


OPCODE_RE = re.compile(r"(?:opcode|op)[-_]?([0-9a-f]{2})(?![0-9a-f])", re.IGNORECASE)
HELPER_RE = re.compile(r"(?:helper[-_])?(20d[0-9a-f]{2})", re.IGNORECASE)


def service_name(name: str) -> str:
    opcode = OPCODE_RE.search(name)
    if opcode:
        return f"opcode_0x{opcode.group(1).lower()}"
    helper = HELPER_RE.search(name)
    if helper:
        return f"helper_0x{helper.group(1).lower()}"
    return "shared_or_unclassified"


def generated_kind(path: Path) -> str:
    name = path.name
    if name.endswith(".summary.json") or name.endswith(".summary.md"):
        return "summary"
    if path.suffix == ".trace":
        return "trace"
    if path.suffix == ".log":
        return "log"
    return "other"


def probe_state(path: Path) -> str | None:
    if path.suffix != ".log" or path.stat().st_size > 1024 * 1024:
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    if "probe: complete" in text:
        return "complete"
    if "probe: start" in text:
        return "started_without_completion_marker"
    return None


def relative_record(path: Path, root: Path) -> dict:
    if path.is_symlink():
        raise ValueError(f"inventory path must not be a symlink: {path}")
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError(f"inventory path escapes root: {path}") from error
    stat = path.stat()
    record = {
        "path": path.relative_to(root).as_posix(),
        "bytes": stat.st_size,
        "kind": generated_kind(path),
        "service": service_name(path.name),
    }
    state = probe_state(path)
    if state:
        record["probe_state"] = state
    return record


def source_inventory(root: Path) -> dict:
    i960 = root / "von" / "i960"
    tools = root / "von" / "tools"
    patches = root / "third_party" / "patches"
    groups = {
        "recovered_c_models": sorted(i960.glob("recovered_sharc_*.c")),
        "probe_stimuli": sorted(tools.glob("probe_sharc_*.lua")),
        "trace_verifiers": sorted(tools.glob("verify_sharc_*.py")),
        "recovered_model_tests": sorted(tools.glob("test_recovered_sharc_*.py")),
        "static_contract_tests": sorted(tools.glob("test_sharc_*.py")),
        "mame_trace_patches": sorted(patches.glob("*-sharc-*.patch")),
    }
    return {
        name: [path.relative_to(root).as_posix() for path in paths]
        for name, paths in groups.items()
    }


def generated_inventory(root: Path) -> list[dict]:
    candidates: set[Path] = set()
    for pattern in ("*sharc*.log", "*sharc*.trace"):
        candidates.update(root.glob(pattern))
    disasm = root / "von" / "build" / "disasm"
    if disasm.exists():
        for pattern in ("*sharc*.log", "*sharc*.trace", "*sharc*.summary.json", "*sharc*.summary.md"):
            candidates.update(disasm.glob(pattern))
    return [relative_record(path, root) for path in sorted(candidates)]


def ledger_inventory(root: Path) -> dict:
    ledger = json.loads((root / "von" / "reconstruction_ledger.json").read_text(encoding="utf-8"))
    image = next(item for item in ledger["images"] if item["name"] == "sharc")
    stages = Counter(item["stage"] for item in image["work_units"])
    classifications = Counter(item["classification"] for item in image["work_units"])
    validation_errors = reconstruction_progress.validate(ledger, root)
    return {
        "entries": len(image["work_units"]),
        "stages": dict(sorted(stages.items())),
        "classifications": dict(sorted(classifications.items())),
        "whole_ledger_validation_errors": validation_errors,
    }


def build_report(root: Path) -> dict:
    generated = generated_inventory(root)
    kinds = Counter(item["kind"] for item in generated)
    services: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0})
    for item in generated:
        services[item["service"]]["files"] += 1
        services[item["service"]]["bytes"] += item["bytes"]
    latest_mtime = max(
        ((root / item["path"]).stat().st_mtime for item in generated),
        default=0,
    )
    return {
        "schema_version": 2,
        "evidence_as_of": datetime.fromtimestamp(latest_mtime, timezone.utc).isoformat(),
        "ledger": ledger_inventory(root),
        "source_artifacts": source_inventory(root),
        "generated_evidence": {
            "files": len(generated),
            "bytes": sum(item["bytes"] for item in generated),
            "kinds": dict(sorted(kinds.items())),
            "services": dict(sorted(services.items())),
            "artifacts": generated,
        },
    }


def markdown(report: dict) -> str:
    ledger = report["ledger"]
    generated = report["generated_evidence"]
    sources = report["source_artifacts"]
    incomplete = [
        item for item in generated["artifacts"]
        if item.get("probe_state") == "started_without_completion_marker"
    ]
    largest = sorted(generated["artifacts"], key=lambda item: item["bytes"], reverse=True)[:15]
    lines = [
        "# SHARC Evidence Inventory",
        "",
        f"Evidence as of: `{report['evidence_as_of']}`",
        "",
        "## Checkpoint",
        "",
        f"- Ledger entries: {ledger['entries']}",
        f"- Stages: {', '.join(f'{key}={value}' for key, value in ledger['stages'].items())}",
        f"- Classifications: {', '.join(f'{key}={value}' for key, value in ledger['classifications'].items())}",
        f"- Whole-ledger validation errors: {len(ledger['whole_ledger_validation_errors'])}",
        f"- Generated artifacts: {generated['files']} files, {generated['bytes']:,} bytes",
        "",
        "## Maintained source artifacts",
        "",
    ]
    for name, paths in sources.items():
        lines.append(f"- `{name}`: {len(paths)}")
    lines.extend(["", "## Generated evidence by service", ""])
    for service, values in generated["services"].items():
        lines.append(f"- `{service}`: {values['files']} files, {values['bytes']:,} bytes")
    lines.extend(["", "## Whole-ledger validation debt", ""])
    if ledger["whole_ledger_validation_errors"]:
        lines.extend(f"- {error}" for error in ledger["whole_ledger_validation_errors"])
    else:
        lines.append("- None")
    lines.extend(["", "## Incomplete small probe outputs", ""])
    if incomplete:
        lines.extend(f"- `{item['path']}` ({item['bytes']:,} bytes)" for item in incomplete)
    else:
        lines.append("- None")
    lines.extend(["", "## Largest generated artifacts", ""])
    lines.extend(f"- `{item['path']}`: {item['bytes']:,} bytes" for item in largest)
    lines.extend([
        "",
        "The JSON inventory contains the complete per-file list. Generated traces are",
        "evidence inputs, not source files; their presence does not promote a ledger entry",
        "from `modeled` to `trace-validated` or `byte-validated`.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    for label, path in (("JSON output", args.json), ("Markdown output", args.markdown)):
        if path is None:
            continue
        if path.is_symlink():
            print(f"SHARC inventory: {label} path must not be a symlink: {path}")
            return 1
        try:
            path.resolve().relative_to(root)
        except (OSError, RuntimeError, ValueError):
            print(f"SHARC inventory: {label} path escapes root: {path}")
            return 1
    try:
        report = build_report(root)
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"SHARC inventory: {error}")
        return 1
    encoded = json.dumps(report, indent=2) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded, encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown(report), encoding="utf-8")
    if not args.json and not args.markdown:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
