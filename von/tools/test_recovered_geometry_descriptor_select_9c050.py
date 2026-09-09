#!/usr/bin/env python3
import ctypes
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


class Input(ctypes.Structure):
    _fields_ = [("first_coordinate_bits", ctypes.c_uint32),
                ("second_coordinate_bits", ctypes.c_uint32),
                ("linked_first_coordinate_bits", ctypes.c_uint32),
                ("linked_second_coordinate_bits", ctypes.c_uint32),
                ("r9", ctypes.c_uint32),
                ("descriptor_gate_passed", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("first_index", ctypes.c_uint32), ("linked_index", ctypes.c_uint32),
                ("first_table_index", ctypes.c_uint32), ("linked_table_index", ctypes.c_uint32),
                ("first_value_562c80", ctypes.c_uint32),
                ("linked_value_562c84", ctypes.c_uint32),
                ("first_fallback", ctypes.c_uint32),
                ("linked_fallback", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-geometry-descriptor-select-") as d:
        so = Path(d) / "geometry-descriptor-select.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_geometry_projection.c"),
                        str(ROOT / "von/i960/recovered_geometry_descriptor_select_9c050.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_descriptor_select_9c050
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(ctypes.c_uint32),
                       ctypes.POINTER(Result)]
        table = (ctypes.c_uint32 * 576)(*[(i * 3 + 1) & 0xffffffff for i in range(576)])
        value = Input(bits(0.0), bits(40.0), bits(0.0), bits(40.0), 9, 1)
        result = Result()
        assert fn(ctypes.byref(value), table, ctypes.byref(result)) == 1
        assert (result.first_index, result.linked_index) == (49, 49)
        assert (result.first_table_index, result.linked_table_index) == (49, 49)
        assert (result.first_value_562c80, result.linked_value_562c84) == (148, 148)
        value.first_coordinate_bits = bits(20000.0)
        assert fn(ctypes.byref(value), table, ctypes.byref(result)) == 1
        assert result.first_fallback == 1 and result.first_table_index == 0
        assert result.first_value_562c80 == 1
        value.first_coordinate_bits = bits(0.0)
        value.linked_first_coordinate_bits = bits(20000.0)
        assert fn(ctypes.byref(value), table, ctypes.byref(result)) == 1
        assert result.first_fallback == 0 and result.linked_fallback == 1
        assert result.linked_table_index == 0
        assert result.linked_value_562c84 == 1
        value.descriptor_gate_passed = 0
        assert fn(ctypes.byref(value), table, ctypes.byref(result)) == 0
        print("PASS: 0x9c050 descriptor grid selection and fallback")


if __name__ == "__main__":
    main()
