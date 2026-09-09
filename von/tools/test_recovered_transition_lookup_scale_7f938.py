#!/usr/bin/env python3
"""Check lookup/scaling preparation at i960 0x7f938."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_lookup_scale_7f938.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "r10", "r11", "lookup_byte", "lookup_index", "lookup_address",
        "raw_value", "value_nonnegative", "clamped_value", "object_state",
        "scalar_bits", "scaled_value", "lookup_table", "clamp_bits",
        "state2_scalar_bits", "default_scalar_bits", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-lookup-scale.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_lookup_scale_7f938
    function.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(2, 3, 4, 0x41200000, 1, 2, 0x41400000, ctypes.byref(plan))
    assert (plan.lookup_index, plan.lookup_address, plan.clamped_value,
            plan.scalar_bits, plan.scaled_value, plan.target) == (
        12, 0x562d98, 0x41200000, 0x40100000, 0x41400000, 0x7f9b0)

    plan = Plan()
    function(0, 1, 7, 0x41100000, 0, 3, 0x40000000, ctypes.byref(plan))
    assert (plan.lookup_index, plan.clamped_value, plan.scalar_bits) == (
        21, 0x42960000, 0x40080000)

print("recovered 0x7f938 lookup-scale vectors: ok")
