#!/usr/bin/env python3
"""Check the literal primary follow-up table at i960 0x7da8c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_primary_table_7da8c.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-primary.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_primary_target_7da8c
    function.argtypes = [ctypes.c_uint32]
    function.restype = ctypes.c_uint32

    expected = [
        0x7DBB8, 0x7DBA8, 0x7DBB8, 0x7DBA8, 0x7DAF0, 0x7DBA8,
        0x7DBB8, 0x7DBA8, 0x7DAF0, 0x7DB00, 0x7DB1C, 0x7DBB8,
        0x7DBA8, 0x7DBB8, 0x7DBC8, 0x7DBB8, 0x7DBA8, 0x7DBB8,
        0x7DBC8, 0x7DBD8, 0x7DBF4, 0x7DC04, 0x7DB2C, 0x7DC98,
    ]
    assert [function(index) for index in range(24)] == expected
    assert function(24) == 0

print("PASS: 0x7da8c primary follow-up table vectors")
