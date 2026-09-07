#!/usr/bin/env python3
"""Verify the recovered stage obstacle boxes against goldens.

Goldens are the render-measured bounds from the t=150 stage export
(stage2-arena.glb, local equals world). Structural invariants pin the
interpretation: every box inside the +/-320 floor shell, pairwise
disjoint XZ footprints, pads containing the (0, +/-60) spawn points, and
the exact OBA set from the export slots.
"""

from __future__ import annotations

import ctypes
import itertools
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_stage_obstacle_boxes.c"

BLOCK, PAD = 0, 1
GOLDENS = [
    (0x0080078E, BLOCK, -156, 0, 164, -124, 20, 236),
    (0x008003DD, BLOCK, -156, 0, -236, -124, 20, -164),
    (0x00800972, BLOCK, 124, 0, 164, 156, 20, 236),
    (0x0080055D, BLOCK, 124, 0, -236, 156, 20, -164),
    (0x00800126, PAD, -36, 0, 44, 36, 20, 76),
    (0x0080009D, PAD, -36, 0, -76, 36, 20, -44),
    (0x0080060E, BLOCK, 204, 0, -36, 236, 20, 36),
]


class Box(ctypes.Structure):
    _fields_ = [("oba", ctypes.c_uint32), ("kind", ctypes.c_uint32),
                ("min_x", ctypes.c_int32), ("min_y", ctypes.c_int32),
                ("min_z", ctypes.c_int32), ("max_x", ctypes.c_int32),
                ("max_y", ctypes.c_int32), ("max_z", ctypes.c_int32)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-obstacle-") as directory:
        library = Path(directory) / "obstacle.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_obstacle_box_count.argtypes = []
        recovered.recovered_obstacle_box_count.restype = ctypes.c_uint32
        recovered.recovered_obstacle_box_at.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(Box)]
        recovered.recovered_obstacle_box_at.restype = ctypes.c_uint32

        assert recovered.recovered_obstacle_box_count() == len(GOLDENS)
        assert recovered.recovered_obstacle_box_at(
            99, ctypes.byref(Box())) == 0, "overrun accepted"
        boxes = []
        for index, golden in enumerate(GOLDENS):
            box = Box()
            assert recovered.recovered_obstacle_box_at(
                index, ctypes.byref(box)) == 1, f"index {index} rejected"
            actual = (box.oba, box.kind, box.min_x, box.min_y, box.min_z,
                      box.max_x, box.max_y, box.max_z)
            assert actual == golden, f"index {index}: {actual} != {golden}"
            boxes.append(actual)
        assert len({box[0] for box in boxes}) == len(boxes), "OBA reused"
        for _, kind, x0, y0, z0, x1, y1, z1 in boxes:
            assert -320 <= x0 < x1 <= 320 and -320 <= z0 < z1 <= 320, \
                "box outside floor shell"
            assert y0 == 0 and y1 == 20, "unexpected box height"
            assert kind in (BLOCK, PAD)
        for first, second in itertools.combinations(boxes, 2):
            assert first[5] <= second[2] or second[5] <= first[2] or \
                first[7] <= second[4] or second[7] <= first[4], \
                f"footprints overlap: {first} vs {second}"
        pads = [box for box in boxes if box[1] == PAD]
        assert len(pads) == 2
        for spawn_x, spawn_z in ((0, 60), (0, -60)):
            assert any(box[2] <= spawn_x <= box[5]
                       and box[4] <= spawn_z <= box[7] for box in pads), \
                f"spawn {(spawn_x, spawn_z)} outside pads"
        print(f"PASS: {len(boxes)} obstacle boxes with shell/disjoint/pad checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
