#!/usr/bin/env python3
"""Check the 0x7e788 packet-10 and classifier setup."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_geometry_packet10_classify_7e788.c"
RUNTIME_SOURCE = ROOT / "von/i960/recovered_runtime_math.c"


# The packet is an inline three-word array, so provide the ABI layout
# explicitly.
class Plan(ctypes.Structure):
    _fields_ = [("record_offset", ctypes.c_uint32),
                ("packet", ctypes.c_uint32 * 3),
                ("fifo_response", ctypes.c_uint32),
                ("response_minus_record_08", ctypes.c_uint32),
                ("response_bit15_set", ctypes.c_uint32),
                ("signed_record_08", ctypes.c_uint32),
                ("signed_object_184", ctypes.c_uint32),
                ("classifier_bias", ctypes.c_uint32),
                ("classifier_input", ctypes.c_uint32),
                ("classifier_band", ctypes.c_uint32),
                ("classifier_target", ctypes.c_uint32),
                ("result_table", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-geometry-packet10-classify.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    str(RUNTIME_SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_geometry_packet10_classify_7e788
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.c_uint16,
                                                  ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(3, 0x100, 0x300, 0x50, 0x9000, 0xfff0, ctypes.byref(plan))
    assert plan.record_offset == 0x60
    assert list(plan.packet) == [10, 0x2b0, 0x200]
    assert plan.response_minus_record_08 == 0x8f00
    assert plan.response_bit15_set == 1
    assert (plan.signed_record_08, plan.signed_object_184) == (0x100, 0xfffffff0)
    assert plan.classifier_input == 0xffafb32c
    assert plan.classifier_band == 6
    assert (plan.classifier_target, plan.result_table) == (0x73508, 0x72660)

    plan = Plan()
    function(0, 0xfff0, 0, 0, 0xfff0, 0x10, ctypes.byref(plan))
    assert plan.response_bit15_set == 0
    assert plan.classifier_input == 0xffffffe0
    assert plan.classifier_band == 9

print("recovered 0x7e788 packet10/classifier vectors: ok")
