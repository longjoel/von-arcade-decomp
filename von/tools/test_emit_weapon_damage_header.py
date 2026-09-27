#!/usr/bin/env python3
"""Hermetic test for the per-fighter weapon damage header generator.

Feeds a tiny type map and damage table to build_rows and checks the emitted
(type, raw, impulse, min, max) rows, including a melee (null) center. No ROMs.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from emit_weapon_damage_header import FIGHTER_ORDER, build_rows  # noqa: E402


def main() -> int:
    records = {
        1: {"index": 1, "damage": 100.0, "impulse": 0.0, "param2": 0, "param3": 999},
        7: {"index": 7, "damage": 175.0, "impulse": -0.25, "param2": 80, "param3": 140},
        19: {"index": 19, "damage": 150.0, "impulse": 0.0, "param2": 0, "param3": 999},
    }
    types = {name: [1, None, 7] for name in FIGHTER_ORDER}
    types["TEMJIN"] = [1, None, 7]
    types["VIPER2"] = [19, 19, 19]
    rows = build_rows(types, records)
    checks = [
        ("row-count", len(rows) == len(FIGHTER_ORDER)),
        ("temjin-left", rows[0][0] == (1, 100, 0.0, 0, 999)),
        ("temjin-center-melee", rows[0][1] == (-1, 0, 0.0, 0, 999)),
        ("temjin-right", rows[0][2] == (7, 175, -0.25, 80, 140)),
        ("viper-left", rows[1][0][1] == 150),
    ]
    failures = [name for name, ok in checks if not ok]
    if failures:
        raise SystemExit(f"FAILED: {failures}")
    print("PASS: weapon damage header generator (rows, raw, melee center)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
