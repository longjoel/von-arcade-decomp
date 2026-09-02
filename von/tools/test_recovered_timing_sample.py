#!/usr/bin/env python3
"""Check the deterministic state update in the 0x18ab0 timing wrapper."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_timing_sample.c"


class State(ctypes.Structure):
    _fields_ = [("latest", ctypes.c_uint32), ("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "libtiming_sample.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        api = ctypes.CDLL(str(library))
        function = api.recovered_timing_sample_update
        function.argtypes = [ctypes.POINTER(State), ctypes.c_uint32, ctypes.c_uint32]
        function.restype = None

        state = State(99, 10, 90)
        function(ctypes.byref(state), 50, 4)
        assert (state.latest, state.low, state.high) == (50, 10, 90)
        function(ctypes.byref(state), 3, 4)
        assert (state.latest, state.low, state.high) == (3, 3, 90)
        function(ctypes.byref(state), 120, 4)
        assert (state.latest, state.low, state.high) == (120, 3, 120)
        function(ctypes.byref(state), 0, 3)
        assert (state.latest, state.low, state.high) == (0, 3, 120)

    print("recovered timing-sample vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
