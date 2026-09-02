#!/usr/bin/env python3
"""Check the recovered 0x783c8 transition wrapper."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_wrapper.c"


class State(ctypes.Structure):
    _fields_ = [("transition", ctypes.c_uint32), ("action", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "libtransition_wrapper.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        api = ctypes.CDLL(str(library))
        function = api.recovered_transition_wrapper
        function.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.POINTER(State)]
        function.restype = None
        table = (ctypes.c_uint32 * 8)(8, 18, 12, 12, 13, 13, 13, 19)
        state = State(0, 0)
        for selector, expected in enumerate(table):
            function(table, selector, ctypes.byref(state))
            assert (state.transition, state.action) == (expected, 5)

    print("recovered transition-wrapper vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
