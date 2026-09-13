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
    by_name = {d["name"]: d for d in docs}

    expect(len(docs) == 10, f"10 fighters, got {len(docs)}")
    temjin = by_name["TEMJIN"]
    expect(temjin["family"] == "0x009e", f"Temjin family {temjin['family']}")
    expect(len(temjin["parts"]) >= 15, f"Temjin parts {len(temjin['parts'])}")
    expect(all(set(p) == {"tpa", "tha", "oba"} for p in temjin["parts"]), "part keys")
    expect(len(temjin["motion"]) > 0, "Temjin motion clips")
    expect(all(c["frames"] > 0 and c["parts"] > 0 for c in temjin["motion"]), "clip fields")

    expect(by_name["APHARMD"]["skeleton"] is not None, "Apharmd skeleton override present")
    expect(by_name["JAGUARANDI"]["family"] is None, "boss family is null")
    print("PASS: offline fighter extraction (10 fighters, parts, motion, skeleton)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
