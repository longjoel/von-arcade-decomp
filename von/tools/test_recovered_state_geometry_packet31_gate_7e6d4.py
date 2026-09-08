#!/usr/bin/env python3
"""Check packet-31 construction and the 0x7e6d4 signed gate."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_geometry_packet31_gate_7e6d4.c"


class Plan(ctypes.Structure):
    _fields_ = [("packet", ctypes.c_uint32 * 5),
                ("fifo_response_r4", ctypes.c_uint32),
                ("first_three_positive", ctypes.c_uint32),
                ("fourth_nonzero", ctypes.c_uint32),
                ("enters_7e788", ctypes.c_uint32),
                ("continues_7e778", ctypes.c_uint32),
                ("packet_target", ctypes.c_uint32),
                ("continue_target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-geometry-packet31-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_geometry_packet31_gate_7e6d4
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.c_int32] * 4 + [
        ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0x10, 0x20, 0x30, 0x40, 0xdeadbeef,
             1, 2, 3, -4, ctypes.byref(plan))
    assert list(plan.packet) == [31, 0x10, 0x20, 0x30, 0x40]
    assert (plan.fifo_response_r4, plan.first_three_positive,
            plan.fourth_nonzero, plan.enters_7e788,
            plan.continues_7e778) == (0xdeadbeef, 1, 1, 1, 0)
    assert (plan.packet_target, plan.continue_target) == (0x884000, 0x7e788)

    for products in ((0, 2, 3, 4), (1, 0, 3, 4), (1, 2, 0, 4),
                     (1, 2, 3, 0)):
        plan = Plan()
        function(0, 0, 0, 0, 0, *products, ctypes.byref(plan))
        assert plan.enters_7e788 == 0
        assert plan.continues_7e778 == 1

print("recovered 0x7e6d4 packet31-gate vectors: ok")
