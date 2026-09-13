#!/usr/bin/env python3
"""Synthetic regression test for attribute_weapon_effects.build_report.

Builds a tiny geometry log with two persistent Temjin parts, one projectile that
spawns on the first, one static muzzle flash on the second, and a stage family
that must be ignored. Checks the classification and mount attribution.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from attribute_weapon_effects import build_report, classify_run, parse_log, split_runs


def object_line(frame: int, oba: int) -> str:
    return (f"[:] vonj_geometry_object: time={frame / 60:.6f} tpa=0009aee8 "
            f"tha=0009afa8 oba={oba:08x} count=00000000 mode=3 source=polygon-rom")


def matrix_line(frame: int, position: tuple[float, float, float]) -> str:
    x, y, z = position
    return (f"[:] vonj_geometry_matrix: time={frame / 60:.6f} "
            f"m=1,0,0,0,1,0,0,0,1 t={x},{y},{z}")


def build_log() -> str:
    lines = []
    for frame in range(0, 101):
        lines.append(matrix_line(frame, (0.0, 0.0, 0.0)))
        lines.append(object_line(frame, 0x009E2A84))   # persistent mech part A
        lines.append(matrix_line(frame, (5.0, 0.0, 0.0)))
        lines.append(object_line(frame, 0x009E2B00))   # persistent mech part B
        lines.append(matrix_line(frame, (500.0, 0.0, 0.0)))
        lines.append(object_line(frame, 0x0084ABCD))   # stage, must be excluded
    for frame in range(10, 31):                        # projectile from part A
        z = (frame - 10) * 15.0
        lines.append(matrix_line(frame, (0.0, 0.0, z)))
        lines.append(object_line(frame, 0x00990001))
    for frame in range(50, 61):                        # muzzle flash on part B
        lines.append(matrix_line(frame, (5.0, 0.0, 0.0)))
        lines.append(object_line(frame, 0x00BB0001))
    return "\n".join(lines) + "\n"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "geometry.log"
        path.write_text(build_log())
        frames = parse_log(path)

    assert len(split_runs({0: (0, 0, 0), 1: (0, 0, 0)})) == 1
    kind, _travel, _peak, disp = classify_run([0, 1, 2, 3], {0: (0, 0, 0), 1: (0, 0, 15), 2: (0, 0, 30), 3: (0, 0, 45)})
    assert kind == "projectile", kind
    assert disp > 25

    report = build_report(frames)
    assert "84" not in report, "stage family leaked into the effect report"
    assert report["99"]["classes"] == {"projectile": 1}, report["99"]
    assert report["99"]["mounts"][0]["mount"] == "9e:009e2a84", report["99"]["mounts"]
    assert report["bb"]["classes"] == {"static": 1}, report["bb"]
    assert report["bb"]["mounts"][0]["mount"] == "9e:009e2b00", report["bb"]["mounts"]

    sided = build_report(frames, sides=True)
    assert sided["99"]["mount_sides"], "side estimation produced no labels"
    print("PASS: attribute_weapon_effects (projectile + flash mount attribution)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
