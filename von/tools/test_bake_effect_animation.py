#!/usr/bin/env python3
"""Hermetic test for the effect-animation reconstruction logic.

No ROMs or captures: builds synthetic object rows (time, oba, tpa, tha, world)
and checks family extraction, tick/step estimation, single-instance chaining
across overlapping spawns, and projectile/effect classification.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bake_effect_animation import (dominant_stream, family_of,  # noqa: E402
                                   sequence_kind, tick_and_step)


def row(time: float, oba: int, world=(0.0, 0.0, 0.0)):
    return (time, oba, oba, oba, world)


def main() -> int:
    checks = []

    def check(name, ok):
        checks.append((name, bool(ok)))

    check("family-extraction", family_of(0x009B8721) == 0x9B)

    tick = 1.0 / 60.0
    # One clean instance: pointer advances one record step per frame.
    instance = [row(tick * i, 1000 + 200 * i) for i in range(6)]
    other = [row(0.50 + tick * i, 5000 + 200 * i) for i in range(2)]
    rows = sorted(instance + other, key=lambda r: r[0])

    est_tick, est_step = tick_and_step(rows)
    check("tick-estimate", abs(est_tick - tick) < 1e-4)
    check("step-estimate", est_step == 200)

    chain, _ = dominant_stream(rows)
    recovered = [entry[1] for entry in chain]
    check("recovers-longer-instance", recovered == [1000, 1200, 1400, 1600, 1800, 2000])

    # Direction can be negative in ROM; the chain must keep time order.
    descending = [row(tick * i, 3000 - 150 * i) for i in range(5)]
    down_chain, _ = dominant_stream(descending)
    check("descending-order",
          [entry[1] for entry in down_chain] == [3000, 2850, 2700, 2550, 2400])

    # World travel decides projectile vs stationary effect.
    travelling = [(0.0, 1, 0, 0, (0.0, 0.0, 0.0)),
                  (0.1, 2, 0, 0, (30.0, 0.0, 40.0))]
    moving, distance = sequence_kind([entry[4] for entry in travelling], 0.1)
    check("projectile-class", moving == "projectile" and distance == 50.0)

    static = [(0.0, 1, 0, 0, (5.0, 5.0, 5.0)),
              (0.05, 2, 0, 0, (5.0, 5.0, 5.0))]
    kind, _ = sequence_kind([entry[4] for entry in static], 0.05)
    check("muzzle-class", kind == "muzzle")

    failures = [name for name, ok in checks if not ok]
    if failures:
        raise SystemExit(f"FAILED: {failures}")
    print("PASS: effect animation reconstruction (family, tick/step, chain, class)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
