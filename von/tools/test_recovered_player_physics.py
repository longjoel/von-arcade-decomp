#!/usr/bin/env python3
"""Verify the recovered player physics constants against goldens.

Goldens are the least-squares fits from the full-bout position tap:
gravity 0.030/frame^2 and jump velocity 1.755 (residual 0.000 on two
independent jumps), walk cap 3.50 u/f (sustained 113-frame segments).
Derived invariants tie the constants back to raw observations: apex
53.1 and full-jump flight near 117 frames.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_player_physics.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-player-physics-") as directory:
        library = Path(directory) / "player-physics.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        for name in ("recovered_player_gravity_milli",
                     "recovered_player_jump_vy_milli",
                     "recovered_player_walk_cap_milli"):
            getattr(recovered, name).argtypes = []
            getattr(recovered, name).restype = ctypes.c_uint32
        gravity = recovered.recovered_player_gravity_milli() / 1000.0
        jump_vy = recovered.recovered_player_jump_vy_milli() / 1000.0
        walk_cap = recovered.recovered_player_walk_cap_milli() / 1000.0
        assert (gravity, jump_vy, walk_cap) == (0.03, 1.755, 3.5), \
            (gravity, jump_vy, walk_cap)
        apex = 1.77 + jump_vy * jump_vy / (2.0 * gravity)
        assert abs(apex - 53.1) < 0.1, f"apex {apex}"
        flight = 2.0 * jump_vy / gravity
        assert abs(flight - 119) < 3.0, f"flight {flight}"
        print(f"PASS: gravity={gravity} jump_vy={jump_vy} "
              f"walk_cap={walk_cap} apex={apex:.2f} flight={flight:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
