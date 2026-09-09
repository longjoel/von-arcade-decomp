#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("active", ctypes.c_uint8 * 32),
                ("preceding_halfword", ctypes.c_uint16 * 32),
                ("current_halfword", ctypes.c_uint16 * 32),
                ("linked_word_0c", ctypes.c_uint32 * 32),
                ("linked_word_10", ctypes.c_uint32 * 32),
                ("linked_word_14", ctypes.c_uint32 * 32),
                ("mode_table_word_24", ctypes.c_uint32 * 256),
                ("mode_table_word_28", ctypes.c_uint32 * 256)]


class Result(ctypes.Structure):
    _fields_ = [("admitted_index", ctypes.c_uint32 * 32),
                ("packet_prefix", (ctypes.c_uint32 * 6) * 32),
                ("admitted_count", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-dual-admission-") as d:
        so = Path(d) / "object-dual-admission.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_object_dual_admission_bd8e0.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_dual_admission_bd8e0
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        input_value = Input()
        input_value.active[0] = 1
        input_value.preceding_halfword[0] = 0x8001
        input_value.current_halfword[0] = 0x7fff
        input_value.linked_word_0c[0] = 0x11111111
        input_value.linked_word_10[0] = 0x22222222
        input_value.linked_word_14[0] = 0x33333333
        input_value.mode_table_word_24[1] = 0x44444444
        input_value.mode_table_word_28[1] = 0x55555555
        input_value.active[1] = 1
        input_value.preceding_halfword[1] = 0x7fff
        input_value.current_halfword[1] = 0
        input_value.active[2] = 1
        input_value.preceding_halfword[2] = 0x8000
        input_value.current_halfword[2] = 0x8000
        input_value.active[3] = 0
        input_value.preceding_halfword[3] = 0x8000
        result = Result()
        fn(ctypes.byref(input_value), ctypes.byref(result))
        assert result.admitted_count == 1
        assert result.admitted_index[0] == 0
        assert list(result.packet_prefix[0]) == [72, 0x11111111,
                                                 0x22222222, 0x33333333,
                                                 0x44444444, 0x55555555]
        print("PASS: paired-object three-part admission predicate")


if __name__ == "__main__":
    main()
