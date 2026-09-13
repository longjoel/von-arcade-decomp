#!/usr/bin/env python3
"""Regression checks for the animation-bake matrix convention.

The geometry trace stores its 3x3 column-major. If the bake reads it as
row-major, ``quat_from_mat`` returns the *inverse* rotation while translations
still reconstruct, producing a correctly-jointed but tangled model. These
checks pin both the convention fix and the FK round-trip.
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location(
        "bake_family_animation", _HERE / "bake_family_animation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expect_close(actual, expected, label, tol=1e-6):
    if abs(actual - expected) > tol:
        raise SystemExit(f"{label}: expected {expected!r}, got {actual!r}")


def expect_vec(actual, expected, label, tol=1e-6):
    for i, (a, e) in enumerate(zip(actual, expected)):
        expect_close(a, e, f"{label}[{i}]", tol)


def to_trace(r, t):
    """Pack a row-major rotation + translation the way a trace stores it."""
    return [r[0], r[3], r[6], r[1], r[4], r[7], r[2], r[5], r[8]], list(t)


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return [c, -s, 0.0, s, c, 0.0, 0.0, 0.0, 1.0]


def mat_t(r):
    return [r[0], r[3], r[6], r[1], r[4], r[7], r[2], r[5], r[8]]


def qmul(a, b):
    return [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1],
            a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
            a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3],
            a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]]


def qrot(q, v):
    tx = 2 * (q[1] * v[2] - q[2] * v[1])
    ty = 2 * (q[2] * v[0] - q[0] * v[2])
    tz = 2 * (q[0] * v[1] - q[1] * v[0])
    return [v[0] + q[3] * tx + (q[1] * tz - q[2] * ty),
            v[1] + q[3] * ty + (q[2] * tx - q[0] * tz),
            v[2] + q[3] * tz + (q[0] * ty - q[1] * tx)]


def quat_to_mat(q):
    x, y, z, w = q
    return [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
            2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
            2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]


def main() -> int:
    bake = _load()

    # A known rotation survives the trace round-trip (not its inverse).
    want = rot_z(0.9)
    m, t = to_trace(want, (4.0, 0.5, -1.0))
    packed = bake.row_major(m, t)
    got = bake.quat_from_mat(bake.orthonormalize(packed[:9]))
    err_fwd = math.sqrt(sum((quat_to_mat(got)[i] - want[i]) ** 2 for i in range(9)))
    expect_close(err_fwd, 0.0, "rotation is not the inverse", 1e-5)

    # Two-bone FK round-trip: position *and* orientation reconstruct.
    rp, rc = rot_z(0.5), rot_z(0.9)
    tp, tc = [1.0, 2.0, 3.0], [4.0, 0.5, -1.0]
    mp, _ = to_trace(rp, tp)
    mc, _ = to_trace(rc, tc)
    wp = bake.row_major(mp, tp)
    wc = bake.row_major(mc, tc)
    local = bake.mat_mul3x4(bake.mat_inv3x4(wp), wc)
    pivot = local[9:12]
    qloc = bake.quat_from_mat(bake.orthonormalize(local[:9]))
    qp = bake.quat_from_mat(bake.orthonormalize(wp[:9]))
    world_t = [tp[i] + qrot(qp, pivot)[i] for i in range(3)]
    world_q = qmul(qp, qloc)
    expect_vec(world_t, tc, "FK translation")
    err = math.sqrt(sum((quat_to_mat(world_q)[i] - rc[i]) ** 2 for i in range(9)))
    expect_close(err, 0.0, "FK rotation is the inverse", 1e-5)

    print("PASS: animation bake matrix convention and FK round-trip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
