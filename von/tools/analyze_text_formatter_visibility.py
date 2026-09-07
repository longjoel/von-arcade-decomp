#!/usr/bin/env python3
"""Report text-cluster unit visibility across single-player capture PC dumps.

Reads every ``*-pcs.txt`` boundary dump in a capture directory (as produced
by ``von/tools/capture_single_player.lua``) and intersects the visited PCs
with the ledger ranges of each ``maincpu.text-*`` code unit. Answers which
formatters and writers actually fired during the coin/start flow, and tags
each unit with its ledger stage so SPECULATIVE (modeled) units stand out
from trace-validated ones.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def preflight(label: str, path: Path, root: Path) -> str | None:
    if path.is_symlink():
        return f"{label} path must not be a symlink: {path}"
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return f"{label} path escapes root: {path}"
    if not path.exists():
        return f"missing {label}: {path}"
    return None


def number(value: str) -> int:
    text = value.strip().lower()
    return int(text, 16 if text.startswith("0x") else 10)


def load_pcs(path: Path) -> set[int]:
    pcs: set[int] = set()
    for line in path.read_text(encoding="ascii").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pcs.add(int(line, 16))
    return pcs


def text_units(ledger: dict) -> list[dict]:
    units = []
    for image in ledger.get("images", []):
        if image.get("name") != "maincpu":
            continue
        for entry in image.get("work_units", []):
            if not isinstance(entry, dict):
                continue
            if entry.get("classification") != "code":
                continue
            if not str(entry.get("id", "")).startswith("maincpu.text-"):
                continue
            addresses: set[int] = set()
            for span in entry.get("ranges", []):
                start, end = number(span["start"]), number(span["end"])
                addresses.update(range(start, end, 4))
            units.append(
                {
                    "id": entry["id"],
                    "stage": entry.get("stage"),
                    "range_size": len(addresses),
                    "addresses": addresses,
                }
            )
    units.sort(key=lambda unit: min(unit["addresses"] or {0}))
    return units


def analyze(capture_dir: Path, ledger: dict) -> dict:
    units = text_units(ledger)
    dumps = sorted(capture_dir.glob("*-pcs.txt"))
    phases = []
    for dump in dumps:
        visited = load_pcs(dump)
        coverage = []
        for unit in units:
            hit = len(unit["addresses"] & visited)
            coverage.append(
                {
                    "id": unit["id"],
                    "stage": unit["stage"],
                    "visited": hit,
                    "total": unit["range_size"],
                    "fired": hit > 0,
                }
            )
        phases.append({"dump": dump.name, "units": coverage})
    return {"units": [unit["id"] for unit in units], "phases": phases}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, default=Path("von/reconstruction_ledger.json"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()
    root = args.root
    errors = [
        error
        for error in (
            preflight("capture directory", args.capture_dir, root),
            preflight("ledger", args.ledger, root),
        )
        if error
    ]
    if args.json is not None:
        error = preflight("JSON output parent", args.json.parent, root)
        if error:
            errors.append(error)
    if errors:
        print("\n".join(errors))
        return 1
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    report = analyze(args.capture_dir, ledger)
    for phase in report["phases"]:
        fired = [u["id"].split("maincpu.text-")[1] for u in phase["units"] if u["fired"]]
        print(f"{phase['dump']}: fired={len(fired)} [{' '.join(fired)}]")
        for unit in phase["units"]:
            if not unit["fired"]:
                print(f"  silent: {unit['id']} [{unit['stage']}]")
    if args.json is not None:
        serializable = {
            "units": report["units"],
            "phases": [
                {"dump": phase["dump"], "units": phase["units"]} for phase in report["phases"]
            ],
        }
        args.json.write_text(json.dumps(serializable, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
