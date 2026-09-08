#!/usr/bin/env python3
"""Check descriptor addressing and state branching at i960 0x7e390."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_geometry_descriptor_7e390.c"


class Plan(ctypes.Structure):
    _fields_ = [("object_byte_offset", ctypes.c_uint32),
                ("descriptor_index", ctypes.c_uint32),
                ("descriptor_offset", ctypes.c_uint32),
                ("descriptor_base", ctypes.c_uint32),
                ("state3_special", ctypes.c_uint32),
                ("descriptor_field4", ctypes.c_uint32),
                ("descriptor_field12", ctypes.c_uint32),
                ("descriptor_field36", ctypes.c_uint32),
                ("scale_constant_40c00000", ctypes.c_uint32),
                ("scale_constant_42f00000", ctypes.c_uint32),
                ("special_scale_3ff80000", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-geometry-descriptor.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_geometry_descriptor_7e390
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint8, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_int16, ctypes.c_uint32]
    function.restype = Plan

    result = function(2, 7, 3, 0x11223344, -12, 0x55667788)
    assert (result.object_byte_offset, result.descriptor_index,
            result.descriptor_offset, result.descriptor_base,
            result.state3_special) == (0x240, 7, 7 * 48, 0x562cb0, 1)
    assert result.descriptor_field12 == 0xfffffff4
    assert (result.scale_constant_40c00000,
            result.scale_constant_42f00000,
            result.special_scale_3ff80000) == (0x40c00000, 0x42f00000,
                                                0x3ff80000)

    assert function(31, 255, 4, 0, 0, 0).state3_special == 0

print("recovered 0x7e390 descriptor-lookup vectors: ok")
