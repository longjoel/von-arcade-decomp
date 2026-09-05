#!/usr/bin/env python3
"""Verify that Linux receives the same presentation events as i960."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_attract_platform.c"


class Platform(ctypes.Structure):
    pass


Present = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32)
Platform._fields_ = [("opaque", ctypes.c_void_p), ("present", Present)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-attract-platform-") as directory:
        library = Path(directory) / "attract-platform.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_attract_present.argtypes = [
            ctypes.POINTER(Platform), ctypes.c_uint32, ctypes.c_uint32
        ]

        events: list[tuple[int, int]] = []

        @Present
        def record(_opaque: int, event: int, tick: int) -> None:
            events.append((event, tick))

        platform = Platform(None, record)
        recovered.recovered_attract_present(ctypes.byref(platform), 1, 4_300_000)
        recovered.recovered_attract_present(ctypes.byref(platform), 5, 6_800_000)
        if events != [(1, 4_300_000), (5, 6_800_000)]:
            raise SystemExit(f"unexpected presentation trace: {events!r}")

    print("PASS: Linux presentation adapter event trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
