#!/usr/bin/env python3
"""Check the follow-up handler table at i960 0x7db80."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_table_7db80.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-table.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_target_7db80
    function.argtypes = [ctypes.c_uint32]
    function.restype = ctypes.c_uint32

    expected = [
        0x7DBA8, 0x7DBA8, 0x7DBB8, 0x7DBB8, 0x7DBC8,
        0x7DBD8, 0x7DBF4, 0x7DC04, 0x7DC98, 0x7DCA8,
    ]
    for index, target in enumerate(expected):
        assert function(index) == target
    assert function(10) == 0
    assert function(0xFFFFFFFF) == 0

print("PASS: 0x7db80 follow-up table vectors")
