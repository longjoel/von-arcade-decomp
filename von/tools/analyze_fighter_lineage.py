#!/usr/bin/env python3
"""Summarize a `fighter_lineage.lua` capture into a per-part classification.

Joins three sources: the lineage log, the emitter->OBA map
(`tools/capture_fighter_emitters.py`), and — when `--trace` is given — the
geometry object stream.  The geometry stream is the ground truth for whether a
part is drawn in a match; the emitter tap is a secondary cross-check that can
miss or mislabel a record.  For every model part the report states whether it is
drawn in-match, select-preview-only, or never drawn, and flags tap/geometry
disagreements.

Usage:
    python3 tools/analyze_fighter_lineage.py \
        --log build/lineage/Viper2/lineage.log \
        --emitters build/lineage/Viper2/emitters.json \
        --tree tools/fighter_trees/viper2.json \
        --parts tools/fighter_parts_rom.json --fighter-key viper2 \
        --trace build/action-roster/Viper2/trace \
        --actions build/action-roster/Viper2/actions.log \
        --out build/lineage/Viper2/tree.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HEADER = re.compile(r"lineage: frame=(\d+) action=(\w+) headers=([0-9a-f]+),([0-9a-f]+) "
                    r"cursor=([0-9a-f]+)")
RECORD = re.compile(r"lineage: frame=(\d+) idx=(\d+) ptr=([0-9a-f]+) parent=(\S+) "
                    r"oba=(\S*) ?(.*)")
GEO_OBJECT = re.compile(r"vonj_geometry_object: time=([\d.]+) .*?oba=([0-9a-fA-F]{8})")
MATCH_BEGIN = re.compile(r"action: t=([\d.]+) .*action=match begin")


def parse_lineage(text: str) -> dict:
    records: dict[int, dict] = {}
    frames = 0
    for line in text.splitlines():
        head = HEADER.match(line)
        if head:
            frames += 1
            continue
        m = RECORD.match(line)
        if not m:
            continue
        frame, index, ptr, parent, obas, rest = m.groups()
        index = int(index)
        rec = records.setdefault(index, {
            "index": index, "ptr": ptr, "parents": Counter(),
            "obas": Counter(), "offsets": defaultdict(Counter),
        })
        rec["ptr"] = ptr
        rec["parents"][parent] += 1
        if obas:
            for token in obas.split(","):
                if ":" in token:
                    rec["obas"][token] += 1
        for token in rest.split():
            if "=" in token:
                key, value = token.split("=", 1)
                rec["offsets"][key][value] += 1
    return {"frames": frames, "records": records}


def _emitted_obas(emitters: dict | None) -> set[str]:
    if not emitters:
        return set()
    if emitters.get("emitted_obas"):
        return {str(v).lower().removeprefix("0x") for v in emitters["emitted_obas"]}
    out: set[str] = set()
    for table in ("g2", "r6"):
        out.update(str(v).lower().removeprefix("0x") for v in emitters.get(table, {}).values())
    return out


def _is_oba(value: str) -> bool:
    try:
        number = int(value, 16)
    except ValueError:
        return False
    return 0x00800000 <= number <= 0x00B00000


def parse_match_start(actions_text: str) -> float | None:
    for line in actions_text.splitlines():
        m = MATCH_BEGIN.search(line)
        if m:
            return float(m.group(1))
    return None


def analyze_geometry(trace: Path, match_start: float,
                     obas: set[str] | None = None) -> dict[str, dict]:
    """Per-part draw coverage from the geometry object stream.

    This is the ground truth for "is the part actually submitted in a match":
    the emitter tap labels transforms but can miss or mislabel a record, while
    the geometry object is what the rasterizer draws.  A sighting at or after
    `match_start` is an in-match draw; anything before is the select preview.
    """
    wanted = {o.lower().removeprefix("0x") for o in obas} if obas else None
    coverage: dict[str, dict] = {}
    with trace.open(errors="replace") as stream:
        for line in stream:
            if "vonj_geometry_object" not in line:
                continue
            m = GEO_OBJECT.search(line)
            if not m:
                continue
            oba = m.group(2).lower()
            if wanted is not None and oba not in wanted:
                continue
            time = float(m.group(1))
            rec = coverage.get(oba)
            if rec is None:
                rec = coverage[oba] = {"count": 0, "tmin": time, "tmax": time,
                                       "match_count": 0, "select_count": 0}
            rec["count"] += 1
            rec["tmin"] = min(rec["tmin"], time)
            rec["tmax"] = max(rec["tmax"], time)
            if time >= match_start:
                rec["match_count"] += 1
            else:
                rec["select_count"] += 1
    return coverage


def classify_parts(model: list[str], emitted: set[str],
                   coverage: dict[str, dict]) -> list[dict]:
    """Cross-check the emitter tap against the geometry draw path."""
    out = []
    for oba in model:
        cov = coverage.get(oba)
        drawn_match = bool(cov and cov.get("match_count", 0) > 0)
        drawn_select = bool(cov and cov.get("select_count", 0) > 0)
        emit_seen = oba in emitted
        if drawn_match:
            status = "match"
        elif drawn_select:
            status = "select-only"
        elif cov:
            status = "other"
        else:
            status = "never"
        out.append({
            "oba": oba,
            "drawn_match": drawn_match,
            "drawn_select": drawn_select,
            "emit_seen": emit_seen,
            "match_count": cov.get("match_count", 0) if cov else 0,
            "select_count": cov.get("select_count", 0) if cov else 0,
            "status": status,
        })
    return out


def analyze(parsed: dict, emitters: dict | None, tree: dict | None) -> dict:
    emitted = _emitted_obas(emitters)
    ptr_map = {}
    if emitters:
        ptr_map = {str(k).lower().removeprefix("0x"): str(v).lower().removeprefix("0x")
                   for k, v in emitters.get("g2", {}).items()}
    records = sorted(parsed["records"].values(), key=lambda r: r["index"])

    def record_obas(rec: dict) -> set[str]:
        found: set[str] = set()
        mapped = ptr_map.get(rec["ptr"].lower())
        if mapped:
            found.add(mapped)
        for token in rec["obas"]:
            value = token.split(":")[-1].lower().removeprefix("0x")
            if _is_oba(value):
                found.add(value)
        for counter in rec["offsets"].values():
            for value in counter:
                if value.startswith("oba:"):
                    found.add(value.split(":")[-1].lower().removeprefix("0x"))
                elif _is_oba(value):
                    found.add(value.lower().removeprefix("0x"))
        return found

    by_index = {rec["index"]: record_obas(rec) for rec in records}
    out_records = []
    emitted_count = 0
    unresolved = []
    non_emitted_parents: list[str] = []
    for rec in records:
        parents = rec["parents"]
        parent_mode, parent_count = (parents.most_common(1)[0] if parents else ("-", 0))
        oba_values = sorted(by_index[rec["index"]])
        is_emitted = bool(by_index[rec["index"]] & emitted) if emitted else None
        if is_emitted:
            emitted_count += 1
        offsets = {key: dict(counter) for key, counter in rec["offsets"].items()}
        entry = {
            "index": rec["index"],
            "ptr": rec["ptr"],
            "oba": ptr_map.get(rec["ptr"].lower()),
            "parent_mode": parent_mode,
            "parent_stable": len(parents) <= 1,
            "parents": dict(parents),
            "obas": oba_values,
            "emitted": is_emitted,
            "offsets": offsets,
        }
        out_records.append(entry)
        if parent_mode.startswith("idx:"):
            target = int(parent_mode.split(":")[1])
            if emitted and not (by_index.get(target, set()) & emitted):
                non_emitted_parents.append(f"{rec['index']}->{target}")
        elif parent_mode not in ("-", "00000000") and not parent_mode.startswith("oba:"):
            unresolved.append(f"{rec['index']}:{parent_mode}")

    reviewed_edges = {}
    if tree:
        for child, parent in tree.get("parents", {}).items():
            reviewed_edges[child.lower().removeprefix("0x")] = parent.lower().removeprefix("0x")

    return {
        "schema": "von-fighter-lineage/1",
        "frames": parsed["frames"],
        "record_count": len(out_records),
        "emitted_oba_count": len(emitted),
        "emitted_obas": sorted(emitted),
        "emitted_records": emitted_count,
        "non_emitted_parent_edges": sorted(set(non_emitted_parents)),
        "unresolved_parents": sorted(set(unresolved)),
        "reviewed_edges": reviewed_edges,
        "records": out_records,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--emitters", type=Path)
    ap.add_argument("--tree", type=Path)
    ap.add_argument("--parts", type=Path,
                    help="tools/fighter_parts_rom.json for the model part set")
    ap.add_argument("--fighter-key", help="lower-case key into --parts, e.g. viper2")
    ap.add_argument("--trace", type=Path,
                    help="geometry capture trace (vonj_geometry_object) for draw coverage")
    ap.add_argument("--actions", type=Path,
                    help="action_schedule log; its 'match begin' time splits preview/match")
    ap.add_argument("--match-start", type=float, default=None,
                    help="explicit match start time (overrides --actions)")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    text = args.log.read_text(encoding="utf-8", errors="replace")
    parsed = parse_lineage(text)
    emitters = json.loads(args.emitters.read_text()) if args.emitters and args.emitters.is_file() else None
    tree = json.loads(args.tree.read_text()) if args.tree and args.tree.is_file() else None
    report = analyze(parsed, emitters, tree)
    emitted = set(report.get("emitted_obas", []))

    model: list[str] = []
    if args.parts and args.fighter_key:
        table = json.loads(args.parts.read_text())
        entry = table.get(args.fighter_key.strip().lower(), {})
        model = sorted(str(p["oba"]).lower().removeprefix("0x") for p in entry.get("parts", []))

    match_start: float | None = args.match_start
    if match_start is None and args.actions and args.actions.is_file():
        match_start = parse_match_start(args.actions.read_text(encoding="utf-8", errors="replace"))
    if args.trace and args.trace.is_file():
        if match_start is None:
            print("lineage: no match start; treating every draw as in-match")
            match_start = 0.0
        coverage = analyze_geometry(args.trace, match_start, obas=set(model) or None)
        report["geometry"] = {
            "trace": str(args.trace),
            "match_start": match_start,
            "parts": coverage,
        }
        if model:
            status = classify_parts(model, emitted, coverage)
            report["part_status"] = status
            report["match_parts"] = [s["oba"] for s in status if s["status"] == "match"]
            report["select_only_parts"] = [s["oba"] for s in status if s["status"] == "select-only"]
            report["never_drawn_parts"] = [s["oba"] for s in status if s["status"] == "never"]
            report["tap_missed_drawn"] = [s["oba"] for s in status
                                          if s["drawn_match"] and not s["emit_seen"]]
            report["tap_phantom"] = sorted(o for o in emitted
                                           if model and o not in {s["oba"] for s in status if s["drawn_match"]})
    elif model:
        report["model_parts"] = model
        report["emitted_parts"] = [o for o in model if o in emitted]
        report["not_emitted_parts"] = [o for o in model if o not in emitted]

    text_out = json.dumps(report, indent=1, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text_out + "\n", encoding="utf-8")
    print(f"lineage: {report['frames']} frames, {report['record_count']} records, "
          f"{report['emitted_records']} emitter-tap records")
    if "match_parts" in report:
        print(f"lineage: drawn in match ({len(report['match_parts'])}): {report['match_parts']}")
        print(f"lineage: select-only ({len(report['select_only_parts'])}): {report['select_only_parts']}")
        if report["never_drawn_parts"]:
            print(f"lineage: never drawn: {report['never_drawn_parts']}")
        if report["tap_missed_drawn"]:
            print(f"lineage: emitter tap missed drawn parts: {report['tap_missed_drawn']}")
        if report["tap_phantom"]:
            print(f"lineage: emitter tap reported non-drawn parts: {report['tap_phantom']}")
    elif report.get("not_emitted_parts") is not None:
        print(f"lineage: model parts without emitter transform: {report['not_emitted_parts']}")
    if report["unresolved_parents"]:
        print(f"lineage: {len(report['unresolved_parents'])} unresolved parent pointers")
    if args.out:
        print(f"lineage: wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
