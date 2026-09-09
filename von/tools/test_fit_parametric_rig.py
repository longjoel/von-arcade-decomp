#!/usr/bin/env python3
"""Contract tests for the parametric-rig fitting math (synthetic data only)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fit_parametric_rig import axis_angle, fit_edge, mat_inv3x4, mat_mul3x4


def rx(deg: float):
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (1.0, 0.0, 0.0, 0.0, c, -s, 0.0, s, c)


def tx(x: float, y: float, z: float):
    return (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, x, y, z)


def main() -> int:
    ident = tx(0.0, 0.0, 0.0)
    m = rx(30.0) + (5.0, -2.0, 7.0)
    back = mat_mul3x4(mat_inv3x4(m), m)
    for got, want in zip(back, ident):
        assert abs(got - want) < 1e-9, f"inverse roundtrip: {back}"

    axis, angle = axis_angle(rx(30.0))
    assert abs(math.degrees(angle) - 30.0) < 1e-9, angle
    assert abs(axis[0] - 1.0) < 1e-9 and abs(axis[1]) < 1e-9, axis

    # Synthetic hinge: parent fixed at origin, child = T(pivot) * Rx(theta).
    pivot = (1.5, -2.5, 4.0)
    parent = ident
    frames = []
    for deg in (-10.0, 0.0, 7.5, 22.0, 30.0):
        frames.append([parent, mat_mul3x4(tx(*pivot), rx(deg) + (0.0, 0.0, 0.0))])
    joint = fit_edge(0, 1, frames)
    assert joint["hinge"], joint
    for got, want in zip(joint["pivot_parent_frame"], pivot):
        assert abs(got - want) < 1e-6, joint["pivot_parent_frame"]
    ax = joint["hinge_axis_parent_frame"]
    assert abs(abs(ax[0]) - 1.0) < 1e-6, ax
    # Series is excursion relative to frame 0 (-10 deg baseline).
    assert joint["angle_min_deg"] == 0.0, joint["angle_min_deg"]
    assert joint["angle_max_deg"] == 40.0, joint["angle_max_deg"]
    assert joint["angle_series_deg"] == [0.0, 10.0, 17.5, 32.0, 40.0], \
        joint["angle_series_deg"]

    # Synthetic ball joint must not pass as a hinge.
    def ry(deg: float):
        t = math.radians(deg)
        c, s = math.cos(t), math.sin(t)
        return (c, 0.0, s, 0.0, 1.0, 0.0, -s, 0.0, c)

    ball = []
    for dx, dy in ((0.0, 0.0), (20.0, 0.0), (20.0, 25.0), (0.0, 25.0)):
        r = mat_mul3x4(rx(dx) + (0.0, 0.0, 0.0), ry(dy) + (0.0, 0.0, 0.0))
        ball.append([parent, mat_mul3x4(tx(*pivot), r + (0.0, 0.0, 0.0))])
    assert not fit_edge(0, 1, ball)["hinge"], "ball joint misclassified"

    # Tap-frame immunity: a common per-frame rigid transform (camera yaw
    # ramp + translation drift) must not change the fit -- fit_edge works
    # on inv(parent)*child, where the common transform cancels exactly.
    def apply_cam(m, phi, d):
        cy, sy = math.cos(phi), math.sin(phi)
        r = m[:9]
        r2 = (cy * r[0] + sy * r[6], cy * r[1] + sy * r[7],
              cy * r[2] + sy * r[8],
              r[3], r[4], r[5],
              -sy * r[0] + cy * r[6], -sy * r[1] + cy * r[7],
              -sy * r[2] + cy * r[8])
        x, y, z = m[9], m[10], m[11]
        p2 = (cy * x + sy * z + d[0], y + d[1], -sy * x + cy * z + d[2])
        return r2 + p2

    cam_frames = []
    for i, f in enumerate(frames):
        phi = math.radians(6.0 * i)
        d = (1.5 * i, -0.5 * i, 0.8 * i)
        cam_frames.append([apply_cam(m, phi, d) for m in f])
    moved = fit_edge(0, 1, cam_frames)
    assert moved["hinge"], moved
    for got, want in zip(moved["pivot_parent_frame"],
                         joint["pivot_parent_frame"]):
        assert abs(got - want) < 1e-9, (got, want)
    assert moved["angle_series_deg"] == joint["angle_series_deg"], \
        (moved["angle_series_deg"], joint["angle_series_deg"])
    assert abs(moved["translation_rms"] - joint["translation_rms"]) < 1e-9, \
        (moved["translation_rms"], joint["translation_rms"])

    print("PASS: parametric-rig fitting math")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
