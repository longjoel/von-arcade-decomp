#!/usr/bin/env python3
"""Validate the ROM-to-C reconstruction ledger and print progress."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from reconstruction_ledger import merged_intervals, number, validate as validate_v2


def address(value: str | int) -> int:
    return number(value)


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def validate(ledger: dict, root: Path) -> list[str]:
    return validate_v2(ledger, root)


def interval_bytes(intervals: list[tuple[int, int]]) -> int:
    return sum(end - start for start, end in merged_intervals(intervals))


def report(ledger: dict) -> str:
    total_code = 0
    matched_code = 0
    lines = []
    for image in ledger.get("images", []):
        code = matched = 0
        code_ranges = [(address(item["start"]), address(item["end"])) for item in image.get("physical_ranges", []) if item.get("classification") == "code"]
        matched_ranges = [(address(r["start"]), address(r["end"])) for unit in image.get("work_units", []) if unit.get("classification") == "code" and unit.get("stage") == "byte-validated" for r in unit.get("ranges", [])]
        code = interval_bytes(code_ranges)
        matched = interval_bytes(matched_ranges)
        total_code += code
        matched_code += matched
        if code:
            lines.append(f"{image['name']}: {matched}/{code} bytes ({matched / code:.2%})")
        else:
            lines.append(f"{image['name']}: 0/0 bytes (no classified executable slices)")
    overall = matched_code / total_code if total_code else 0.0
    header = f"overall: {matched_code}/{total_code} executable bytes ({overall:.2%})"
    return "\n".join([header, *lines])


def semantic_report(ledger: dict) -> str:
    """Report C-represented code separately from the byte-match headline."""
    total_code = 0
    represented_code = 0
    lines = []
    for image in ledger.get("images", []):
        code = represented = 0
        code = interval_bytes([(address(item["start"]), address(item["end"])) for item in image.get("physical_ranges", []) if item.get("classification") == "code"])
        represented = interval_bytes([(address(r["start"]), address(r["end"])) for unit in image.get("work_units", []) if unit.get("classification") == "code" and unit.get("stage") in {"modeled", "integrated", "trace-validated", "byte-validated"} for r in unit.get("ranges", [])])
        total_code += code
        represented_code += represented
        if code:
            lines.append(
                f"{image['name']}: {represented}/{code} C-represented bytes "
                f"({represented / code:.2%})"
            )
        else:
            lines.append(f"{image['name']}: 0/0 bytes (no classified executable slices)")
    overall = represented_code / total_code if total_code else 0.0
    header = (
        f"overall: {represented_code}/{total_code} C-represented executable bytes "
        f"({overall:.2%}); this is not byte-validated coverage"
    )
    return "\n".join([header, *lines])


def find_slice(ledger: dict, identifier: str) -> tuple[dict, dict]:
    try:
        image_name, slice_name = identifier.split("/", 1)
    except ValueError as exc:
        raise ValueError("slice must be identified as IMAGE/SLICE") from exc
    for image in ledger.get("images", []):
        if image.get("name") != image_name:
            continue
        for work_unit in image.get("work_units", []):
            if work_unit.get("name") == slice_name or work_unit.get("id") == identifier.replace("/", ".", 1):
                return image, work_unit
    raise ValueError(f"unknown work unit: {identifier}")


def compare_slice(
    ledger: dict, identifier: str, original_path: Path, generated_path: Path, generated_offset: int
) -> tuple[str, bool]:
    image, slice_entry = find_slice(ledger, identifier)
    del image
    ranges = slice_entry.get("ranges", [])
    if len(ranges) != 1:
        raise ValueError("comparison requires a work unit with exactly one semantic range")
    start = address(ranges[0]["start"])
    size = address(ranges[0]["end"]) - start
    with original_path.open("rb") as stream:
        stream.seek(start)
        original = stream.read(size)
    with generated_path.open("rb") as stream:
        stream.seek(generated_offset)
        generated = stream.read(size)
    if len(original) != size or len(generated) != size:
        raise ValueError(f"could not read {size} bytes from both images")
    original_hash = hashlib.sha256(original).hexdigest()
    generated_hash = hashlib.sha256(generated).hexdigest()
    matching = sum(left == right for left, right in zip(original, generated))
    status = "MATCH" if original == generated else "MISMATCH"
    output = (
        f"{identifier}: {status}; {matching}/{size} bytes equal\n"
        f"original sha256: {original_hash}\n"
        f"generated sha256: {generated_hash}"
    )
    return output, original == generated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=Path("von/reconstruction_ledger.json"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--report", action="store_true", help="print the progress report")
    parser.add_argument(
        "--semantic-report",
        action="store_true",
        help="print modeled-or-later C coverage; not the byte-match metric",
    )
    parser.add_argument("--compare", metavar="IMAGE/SLICE", help="compare one ledger slice")
    parser.add_argument("--original", type=Path, help="original flat firmware image")
    parser.add_argument("--generated", type=Path, help="generated flat firmware image")
    parser.add_argument(
        "--generated-offset",
        type=lambda value: int(value, 0),
        default=0,
        help="offset of the generated slice, default: 0",
    )
    args = parser.parse_args()
    try:
        ledger = load(args.ledger)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read ledger: {exc}", file=sys.stderr)
        return 1
    errors = validate(ledger, args.root)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    if args.compare:
        if not args.original or not args.generated:
            parser.error("--compare requires --original and --generated")
        try:
            output, matches = compare_slice(
                ledger, args.compare, args.original, args.generated, args.generated_offset
            )
            print(output)
            if not matches:
                return 1
        except (OSError, ValueError) as exc:
            print(f"error: comparison failed: {exc}", file=sys.stderr)
            return 1
    else:
        print(semantic_report(ledger) if args.semantic_report else report(ledger) if args.report else "ledger valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
