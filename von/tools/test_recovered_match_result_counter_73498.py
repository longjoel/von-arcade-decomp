#!/usr/bin/env python3
"""Validate the bounded/overflow transition at i960 0x73498."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_result_counter_73498.c"


class Output(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("pair_first", "pair_second", "cleared_504d9c", "cleared_504da4")]


with tempfile.TemporaryDirectory(prefix="von-match-counter-73498-") as directory:
    library = pathlib.Path(directory) / "counter.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    function = ctypes.CDLL(str(library)).recovered_match_result_counter_73498
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Output)]
    function.restype = None

    output = Output()
    function(7, 3, 10, 0, 0, ctypes.byref(output))
    assert (output.pair_first, output.pair_second,
            output.cleared_504d9c, output.cleared_504da4) == (7, 4, 0, 0)

    function(7, 10, 10, 0x1234, 99, ctypes.byref(output))
    assert (output.pair_first, output.pair_second,
            output.cleared_504d9c, output.cleared_504da4) == (7, 0xffffffff, 1, 1)

    function(7, 10, 10, 0, 0, ctypes.byref(output))
    assert (output.cleared_504d9c, output.cleared_504da4) == (1, 0)
    function(7, 10, 10, 0xffffffff, 99, ctypes.byref(output))
    assert (output.cleared_504d9c, output.cleared_504da4) == (1, 1)
    function(7, 0xffffffff, 0xffffffff, 0xffffffff, 100, ctypes.byref(output))
    assert (output.pair_second, output.cleared_504d9c,
            output.cleared_504da4) == (0, 0, 0)

print("PASS: 0x73498 bounded and overflow counter transitions")
