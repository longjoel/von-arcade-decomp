#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("object_table", (ctypes.c_uint8 * 32) * 2),
                ("record_halfword", (ctypes.c_uint16 * 32) * 2),
                ("object_word_68", ctypes.c_uint32 * 2)]


class Result(ctypes.Structure):
    _fields_ = [("accepted_object", ctypes.c_uint32 * 64),
                ("accepted_index", ctypes.c_uint32 * 64),
                ("dispatch_target", ctypes.c_uint32 * 64),
                ("suppressed_bit8", ctypes.c_uint32 * 64),
                ("rejected_above_cc", ctypes.c_uint32 * 64),
                ("accepted_count", ctypes.c_uint32),
                ("suppressed_count", ctypes.c_uint32),
                ("rejected_count", ctypes.c_uint32),
                ("final_global_565e20", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-pair-scan-") as d:
        so = Path(d) / "object-pair-scan.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_object_pair_scan_bece0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_pair_scan_bece0
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(ctypes.c_uint32),
                       ctypes.POINTER(Result)]
        value = Input()
        value.object_word_68[:] = (0x11111111, 0x22222222)
        for object_index in range(2):
            for index in range(32):
                value.object_table[object_index][index] = 0xcd
        value.object_table[0][0] = 1
        value.object_table[0][1] = 0xcd
        value.object_table[0][2] = 2
        value.record_halfword[0][2] = 0x100
        value.object_table[1][3] = 0xcc
        value.object_table[1][4] = 0xce
        dispatch = (ctypes.c_uint32 * 256)(*[(0x9000 + i * 4) for i in range(256)])
        result = Result()
        fn(ctypes.byref(value), dispatch, ctypes.byref(result))
        assert result.accepted_count == 2
        assert list(result.accepted_object[:2]) == [0, 1]
        assert list(result.accepted_index[:2]) == [0, 3]
        assert list(result.dispatch_target[:2]) == [0x9004, 0x9330]
        assert result.suppressed_count == 1 and result.suppressed_bit8[0] == 2
        assert result.rejected_count == 61
        assert list(result.rejected_above_cc[:2]) == [1, 3]
        assert result.final_global_565e20 == 0x22222222
        print("PASS: paired object scan admission, suppression, and dispatch")


if __name__ == "__main__":
    main()
