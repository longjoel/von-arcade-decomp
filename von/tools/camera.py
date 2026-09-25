#!/usr/bin/env python3
"""Camera tools: parse the per-frame capture log and factor the camera out.

The geometry matrices a capture records are camera-relative (Model 2 has no
view command; the i960 bakes the camera into each object's accepted matrix). The
`camera.log` sidecar written by `von/tools/action_schedule.lua` records the eye
and target per frame, from which the view is rebuilt and removed:

    model = inv(view) * device

All matrices here are 3x4 row-major column-vector affines
`[r00 r01 r02 tx  r10 r11 r12 ty  r20 r21 r22 tz]`, matching
`von-reference-animation/1`.

  python3 tools/camera.py --camera-log .../camera.log --trace .../trace \
      --root 009e2a84 --time 37.0
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

CAMERA = re.compile(r"camera: t=([0-9.]+) frame=(\d+)(?: action=\w+)? "
                    r"eye=([-\d.,]+) target=([-\d.,]+) dist=([-\d.]+)")
MATRIX = re.compile(r"vonj_geometry_matrix: (?:seq=\d+ )?time=([0-9.e+-]+) "
                    r"m=([^ ]+) t=([^ ]+)")
OBJECT = re.compile(r"vonj_geometry_object: (?:seq=\d+ )?time=([0-9.e+-]+) "
                    r".*?oba=([0-9a-f]{8})")


def _vec(text: str) -> tuple[float, float, float]:
    values = [float(v) for v in text.split(",")]
    return values[0], values[1], values[2]


def parse_camera_log(path: Path) -> list[dict]:
    frames = []
    for line in path.read_text(errors="ignore").splitlines():
        match = CAMERA.search(line)
        if match:
            frames.append({"t": float(match.group(1)), "frame": int(match.group(2)),
                           "eye": _vec(match.group(3)), "target": _vec(match.group(4)),
                           "dist": float(match.group(5))})
    return frames


def nearest(frames: list[dict], time: float) -> dict:
    return min(frames, key=lambda frame: abs(frame["t"] - time))


def nearest_frame(frames: list[dict], frame: int) -> dict:
    """Nearest frame with a live camera (the boot frames read as zeros)."""
    live = [f for f in frames if any(abs(v) > 1e-6 for v in f["eye"])]
    pool = live or frames
    return min(pool, key=lambda f: abs(f["frame"] - frame))


def mul(a: list[float], b: list[float]) -> list[float]:
    """Compose two 3x4 row-major affines: a then b (column-vector)."""
    def rot(m, r, c):
        return m[r * 4 + c]

    def trans(m, r):
        return m[r * 4 + 3]

    out = [0.0] * 12
    for r in range(3):
        for c in range(3):
            out[r * 4 + c] = sum(rot(a, r, k) * rot(b, k, c) for k in range(3))
        out[r * 4 + 3] = trans(a, r) + sum(rot(a, r, k) * trans(b, k) for k in range(3))
    return out


def inv_rigid(a: list[float]) -> list[float]:
    """Inverse of a 3x4 row-major rigid affine."""
    out = [a[0], a[4], a[8], 0.0, a[1], a[5], a[9], 0.0, a[2], a[6], a[10], 0.0]
    for r in range(3):
        out[r * 4 + 3] = -sum(out[r * 4 + c] * a[c * 4 + 3] for c in range(3))
    return out


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    length = math.sqrt(sum(v * v for v in a))
    return (a[0] / length, a[1] / length, a[2] / length)


def view_matrix(eye, target, up=(0.0, 1.0, 0.0)) -> list[float]:
    """World -> camera. Forward maps to +z (the geometry engine's depth axis).

    The basis is right-handed: right = up x forward, up' = forward x right, so
    `det(right, up', forward) = +1` and no reflection is introduced.
    """
    f = _norm((target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]))
    r = _norm(_cross(up, f))
    u = _cross(f, r)
    return [r[0], r[1], r[2], -(r[0] * eye[0] + r[1] * eye[1] + r[2] * eye[2]),
            u[0], u[1], u[2], -(u[0] * eye[0] + u[1] * eye[1] + u[2] * eye[2]),
            f[0], f[1], f[2], -(f[0] * eye[0] + f[1] * eye[1] + f[2] * eye[2])]


def row_major(matrix: str, translation: str) -> list[float]:
    m = [float(v) for v in matrix.split(",")]
    t = [float(v) for v in translation.split(",")]
    return [m[0], m[3], m[6], t[0], m[1], m[4], m[7], t[1], m[2], m[5], m[8], t[2]]


def trace_root_matrices(path: Path, root: str, time: float, window: float = 0.02) -> list[list[float]]:
    current: list[float] | None = None
    out: list[list[float]] = []
    best = None
    for line in path.open(errors="ignore"):
        matrix = MATRIX.search(line)
        if matrix:
            current = row_major(matrix.group(2), matrix.group(3))
            continue
        obj = OBJECT.search(line)
        if obj:
            t = float(obj.group(1))
            if obj.group(2) == root and abs(t - time) <= window:
                if best is None or abs(t - time) < abs(best - time):
                    best = t
                    out = []
                if abs(t - best) < 1e-9 and current is not None:
                    out.append(current)
    return out


def model_space(device: list[float], view: list[float]) -> list[float]:
    return mul(inv_rigid(view), device)


def _self_test() -> None:
    view = view_matrix((1.0, 2.0, 3.0), (4.0, 5.0, 6.0))
    identity = mul(inv_rigid(view), view)
    for r in range(3):
        for c in range(3):
            assert abs(identity[r * 4 + c] - (1.0 if r == c else 0.0)) < 1e-9
        assert abs(identity[r * 4 + 3]) < 1e-9


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera-log", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--time", type=float, required=True)
    args = parser.parse_args()
    _self_test()

    frames = parse_camera_log(args.camera_log)
    frame = nearest(frames, args.time)
    view = view_matrix(frame["eye"], frame["target"])
    print(f"t={frame['t']:.3f} eye={frame['eye']} target={frame['target']}")
    for device in trace_root_matrices(args.trace, args.root.lower(), frame["t"]):
        world = model_space(device, view)
        print(f"  device t=({device[3]:8.2f},{device[7]:8.2f},{device[11]:8.2f}) "
              f"-> world t=({world[3]:8.2f},{world[7]:8.2f},{world[11]:8.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
