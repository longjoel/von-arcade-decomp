#!/usr/bin/env python3
"""Check the deterministic entry gate at i960 0x78dd0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_entry_gate_78dd0.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libgeometry-entry-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_geometry_entry_route_78dd0
    function.argtypes = [ctypes.c_uint32]
    function.restype = ctypes.c_uint32
    target = api.recovered_geometry_entry_target_78dd0
    target.argtypes = [ctypes.c_uint32]
    target.restype = ctypes.c_uint32
    for object_state in range(10):
        expected = 1 if object_state in (2, 4) else 0
        assert function(object_state) == expected
        assert target(expected) == (0x7cbc0 if expected else 0x78de4)

print("recovered 0x78dd0 geometry entry-gate vectors: ok")
