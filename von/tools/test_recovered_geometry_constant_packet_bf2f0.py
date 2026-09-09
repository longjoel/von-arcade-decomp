#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("object_byte_0", ctypes.c_uint32),
                ("object_halfword_4", ctypes.c_uint32),
                ("mode_503a08", ctypes.c_uint32),
                ("readback_802008", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [("accepted", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 8),
                ("fifo_count", ctypes.c_uint32),
                ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32),
                ("window_address", ctypes.c_uint32 * 4),
                ("window_word", ctypes.c_uint32 * 4),
                ("completion_word", ctypes.c_uint32),
                ("publication_address", ctypes.c_uint32),
                ("publication_value", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-geometry-constant-packet-") as d:
        so = Path(d) / "geometry-constant-packet.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_geometry_constant_packet_bf2f0.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_constant_packet_bf2f0
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(ctypes.c_uint32),
                       ctypes.POINTER(Plan)]
        table = (ctypes.c_uint32 * 256)()
        table[3] = 0x2400
        plan = Plan()
        input_value = Input(0x103, 0x2400, 2, 0x12345678)
        fn(ctypes.byref(input_value), table, ctypes.byref(plan))
        assert plan.accepted == 1 and plan.fifo_count == 8
        assert list(plan.fifo_word) == [5, 16, 18, 0, 0, 0x3f800000, 58, 0x12345678]
        assert list(plan.window_word) == [0, 0x40005c, 0x8f31a0, 0]
        assert plan.publication_value == 0x123456ac
        input_value.object_halfword_4 = 0x23ff
        fn(ctypes.byref(input_value), table, ctypes.byref(plan))
        assert plan.accepted == 1
        input_value.object_halfword_4 = 0x23fe
        fn(ctypes.byref(input_value), table, ctypes.byref(plan))
        assert plan.accepted == 0
        input_value.object_halfword_4 = 0x2400
        input_value.mode_503a08 = 1
        fn(ctypes.byref(input_value), table, ctypes.byref(plan))
        assert plan.accepted == 0
        print("PASS: fixed geometry packet gate, match, and publication")


if __name__ == "__main__":
    main()
