#!/usr/bin/env python3
"""Stream a MAME trace into compact JSON/Markdown evidence and optionally gzip it."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path


EVENT_RE = re.compile(r"^\[[^]]*\]\s+(?P<event>[A-Za-z0-9_]+):\s*(?P<body>.*)$")
HEX_RE = re.compile(r"(?<![A-Za-z0-9])[0-9a-fA-F]{4,}(?![A-Za-z0-9])")
DECIMAL_RE = re.compile(r"(?<![A-Za-z0-9])[0-9]{3,}(?![A-Za-z0-9])")


def signature(line: str) -> str:
    """Collapse changing addresses/counters while keeping event meaning readable."""
    return DECIMAL_RE.sub("<n>", HEX_RE.sub("<hex>", line.strip()))


def summarize(path: Path) -> dict:
    digest = hashlib.sha256()
    event_counts: Counter[str] = Counter()
    signatures: Counter[str] = Counter()
    runs: Counter[str] = Counter()
    first: list[str] = []
    last: list[str] = []
    lines = 0
    previous = ""
    run_length = 0

    def finish_run() -> None:
        nonlocal previous, run_length
        if run_length > 1:
            runs[previous] += run_length

    with path.open("rb") as stream:
        for raw in stream:
            digest.update(raw)
            line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            lines += 1
            if len(first) < 12:
                first.append(line)
            last.append(line)
            if len(last) > 12:
                last.pop(0)
            event = EVENT_RE.match(line)
            event_counts[event.group("event") if event else "unstructured"] += 1
            current = signature(line)
            signatures[current] += 1
            if current == previous:
                run_length += 1
            else:
                finish_run()
                previous = current
                run_length = 1
    finish_run()
    return {
        "schema_version": 1,
        "source": str(path),
        "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
        "lines": lines,
        "event_counts": dict(sorted(event_counts.items())),
        "top_signatures": [
            {"signature": item, "lines": count}
            for item, count in signatures.most_common(24)
        ],
        "collapsed_runs": [
            {"signature": item, "lines": count}
            for item, count in runs.most_common(24)
        ],
        "first_lines": first,
        "last_lines": last,
    }


def markdown(report: dict) -> str:
    lines = [
        "# MAME Trace Summary",
        "",
        f"- Source: `{report['source']}`",
        f"- Size: {report['bytes']:,} bytes",
        f"- SHA-256: `{report['sha256']}`",
        f"- Lines: {report['lines']:,}",
        "",
        "## Event Families",
        "",
    ]
    lines.extend(f"- `{event}`: {count:,}" for event, count in report["event_counts"].items())
    lines.extend(["", "## Repeated Runs", ""])
    if report["collapsed_runs"]:
        lines.extend(
            f"- {record['lines']:,} lines: `{record['signature']}`"
            for record in report["collapsed_runs"]
        )
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def archive(path: Path) -> Path:
    target = path.with_suffix(path.suffix + ".gz")
    if target.exists():
        raise FileExistsError(f"archive already exists: {target}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=target.name + ".", dir=path.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with path.open("rb") as source, gzip.open(temporary, "wb", compresslevel=9) as output:
            while chunk := source.read(1024 * 1024):
                output.write(chunk)
        os.replace(temporary, target)
        path.unlink()
    finally:
        temporary.unlink(missing_ok=True)
    return target


def path_error(label: str, path: Path, root: Path, *, output: bool = False) -> str | None:
    if path.is_symlink():
        return f"{label} path must not be a symlink: {path}"
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return f"{label} path escapes root: {path}"
    if not output and not path.is_file():
        return f"missing {label}: {path}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--markdown", dest="markdown_path", type=Path)
    parser.add_argument("--root", type=Path,
                        help="root that trace and summary paths must remain within (defaults to trace parent)")
    parser.add_argument("--archive", action="store_true", help="replace raw trace with a gzip archive")
    args = parser.parse_args()
    root = (args.root or args.trace.parent).resolve()
    json_path = args.json_path or args.trace.with_suffix(args.trace.suffix + ".summary.json")
    markdown_path = args.markdown_path or args.trace.with_suffix(args.trace.suffix + ".summary.md")
    for label, path, output in (("trace", args.trace, False),
                                ("JSON output", json_path, True),
                                ("Markdown output", markdown_path, True)):
        error = path_error(label, path, root, output=output)
        if error:
            print(f"Trace summary: {error}")
            return 1
    report = summarize(args.trace)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown(report), encoding="utf-8")
    if args.archive:
        archived = archive(args.trace)
        print(f"Archived raw trace: {archived}")
    print(f"Trace summary: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
