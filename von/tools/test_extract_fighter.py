#!/usr/bin/env python3
"""Regression checks for the offline per-fighter ROM extractor."""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROM = _HERE.parent / "artifacts"
_TREES = _HERE.parent / "rigs"


def _load():
    spec = importlib.util.spec_from_file_location("extract_fighter", _HERE / "extract_fighter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expect(cond, label):
    if not cond:
        raise SystemExit(f"FAIL: {label}")


def main() -> int:
    if not (_ROM / "epr-18664b.15").is_file():
        raise SystemExit(f"ROM set missing under {_ROM}")
    extract = _load()
    with tempfile.TemporaryDirectory() as td:
        docs = extract.extract(_ROM, Path(td), _TREES)
    by_name = {d["identity"]["name"]: d for d in docs}

    expect(len(docs) == 10, f"10 fighters, got {len(docs)}")
    temjin = by_name["TEMJIN"]
    ident = temjin["identity"]
    expect(ident["family"] == "0x009e", f"Temjin family {ident['family']}")
    expect(ident["fighter_id"] == "0x1331", f"Temjin fighter_id {ident['fighter_id']}")
    expect(temjin["model"]["parts"] and
           all(set(p) == {"tpa", "tha", "oba"} for p in temjin["model"]["parts"]),
           "Temjin part keys")
    expect(temjin["model"]["pose_markers"], "Temjin pose markers")
    expect(temjin["model"]["directory"]["range_start"].startswith("0x"), "Temjin directory range")
    expect(temjin["model"]["directory_parts"], "Temjin directory parts")
    groups = temjin["profile"]["part_groups"]
    expect(groups and all(set(p) == {"tpa", "tha", "param", "oba"}
                          for g in groups for p in g["parts"]),
           f"Temjin profile part groups {groups}")
    expect(temjin["motion"]["clip_count"] > 0, "Temjin motion clips")
    expect(temjin["motion"]["total_frames"] > 1000, "Temjin motion frames")

    weapon = temjin["weapons"]
    expect(weapon is not None and "BEAM RIFLE" in weapon["names"], f"Temjin weapon {weapon}")

    # Bosses have no family prefix but do have model-directory parts.
    boss = by_name["JAGUARANDI"]["model"]["directory_parts"]
    expect(len(boss) > 0, "Jaguarandi directory parts recovered")
    expect(by_name["APHARMD"]["skeleton"] is not None, "Apharmd skeleton override present")
    # The model groups merge a fighter's primary group with its tpa-adjacent
    # continuation groups (Apharmd's arms + leg chain, Dorkas's two groups).
    expect(len(by_name["APHARMD"]["model"]["parts"]) == 17, "Apharmd 17-part model")
    expect(len(by_name["DORKAS"]["model"]["parts"]) == 15, "Dorkas 15-part model")
    expect(len(temjin["model"]["parts"]) == 19, "Temjin 19-part model")
    print("PASS: offline fighter extraction (identity, parts, markers, motion, weapons, skeleton)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
