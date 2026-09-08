#!/usr/bin/env python3
"""Validate the status-gated 0x735d0 dispatch table."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_result_state_dispatch_735d0.c"


with tempfile.TemporaryDirectory(prefix="von-match-dispatch-735d0-") as directory:
    library = pathlib.Path(directory) / "dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    function = ctypes.CDLL(str(library)).recovered_match_result_state_dispatch_735d0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = ctypes.c_uint32

    assert function(1, 0) == 0x853C8
    assert function(0, 34) == 0x74848
    expected = [
        0x74848, 0x736A0, 0x737C8, 0x73900, 0x73A34, 0x73B68,
        0x73C98, 0x73DCC, 0x74148, 0x744EC, 0x73FDC, 0x73FFC,
        0x7402C, 0x7408C, 0x740EC, 0x740F8, 0x74104, 0x74110,
        0x7411C, 0x74138, 0x7415C, 0x74178, 0x74194, 0x745BC,
        0x74848, 0x745E4, 0x7460C, 0x74634, 0x74674, 0x746F4,
        0x74754, 0x7479C, 0x747E4, 0x74848,
    ]
    assert [function(0, index) for index in range(34)] == expected

print("PASS: 0x735d0 status gate and 34-entry dispatch table")
