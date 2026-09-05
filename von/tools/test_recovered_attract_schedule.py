#!/usr/bin/env python3
"""Run the shared boot/title scheduler natively on Linux."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_attract_schedule.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-attract-schedule-") as directory:
        library = Path(directory) / "attract-schedule.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        schedule = ctypes.CDLL(str(library))
        schedule.recovered_attract_next_phase.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        schedule.recovered_attract_next_phase.restype = ctypes.c_uint32

        thresholds = (4_300_000, 4_900_000, 5_200_000, 5_800_000, 6_800_000)
        for phase, threshold in enumerate(thresholds):
            before = schedule.recovered_attract_next_phase(threshold - 1, phase)
            after = schedule.recovered_attract_next_phase(threshold, phase)
            if before != phase or after != phase + 1:
                raise SystemExit(
                    f"phase boundary mismatch phase={phase} threshold={threshold}: "
                    f"before={before} after={after}"
                )
        if schedule.recovered_attract_next_phase(0xFFFFFFFF, 5) != 5:
            raise SystemExit("terminal phase advanced unexpectedly")

    print("PASS: Linux/i960 shared boot-title-attract scheduler boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
