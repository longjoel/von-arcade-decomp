#!/usr/bin/env python3
"""Check the deterministic state update in the 0x18ab0 timing wrapper."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_timing_sample.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class State(ctypes.Structure):
    _fields_ = [("latest", ctypes.c_uint32), ("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]


def main() -> int:
    listing = LISTING.read_text(encoding="utf-8")
    for address, fragment in (
        ("18ab0", "bal\t0x28de8"),
        ("18af4", "call\t0x2d60"),
    ):
        line = next((line for line in listing.splitlines()
                     if f"{address}:" in line), "")
        if fragment not in line:
            raise SystemExit(
                f"timing wrapper edge {address} missing {fragment}"
            )

    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "libtiming_sample.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        api = ctypes.CDLL(str(library))
        function = api.recovered_timing_sample_update
        function.argtypes = [ctypes.POINTER(State), ctypes.c_uint32, ctypes.c_uint32]
        function.restype = None

        post_calls = []
        callback_type = ctypes.CFUNCTYPE(None)
        post_service = callback_type(lambda: post_calls.append(True))
        chained = api.recovered_timing_sample_update_and_post_service
        chained.argtypes = [ctypes.POINTER(State), ctypes.c_uint32,
                            ctypes.c_uint32, callback_type]
        chained.restype = None

        state = State(99, 10, 90)
        function(ctypes.byref(state), 50, 4)
        assert (state.latest, state.low, state.high) == (50, 10, 90)
        function(ctypes.byref(state), 3, 4)
        assert (state.latest, state.low, state.high) == (3, 3, 90)
        function(ctypes.byref(state), 120, 4)
        assert (state.latest, state.low, state.high) == (120, 3, 120)
        function(ctypes.byref(state), 0, 3)
        assert (state.latest, state.low, state.high) == (0, 3, 120)
        chained(ctypes.byref(state), 7, 3, post_service)
        assert (state.latest, state.low, state.high) == (7, 3, 120)
        assert len(post_calls) == 1
        chained(ctypes.byref(state), 200, 4, post_service)
        assert (state.latest, state.low, state.high) == (200, 3, 200)
        assert len(post_calls) == 2

    print("recovered timing-sample vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
