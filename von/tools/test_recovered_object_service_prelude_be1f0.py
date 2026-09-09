#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("active", (ctypes.c_uint8 * 32) * 2),
                ("record_halfword", (ctypes.c_uint16 * 32) * 2),
                ("status_48", ctypes.c_uint32 * 2),
                ("status_callback_result", ctypes.c_uint32 * 2)]


class Result(ctypes.Structure):
    _fields_ = [("service_object", ctypes.c_uint32 * 128),
                ("service_index", ctypes.c_uint32 * 128),
                ("service_selector", ctypes.c_uint32 * 128),
                ("service_call_count", ctypes.c_uint32),
                ("status_call_object", ctypes.c_uint32 * 2),
                ("status_call_count", ctypes.c_uint32),
                ("status_publication", ctypes.c_uint32 * 2)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-service-prelude-") as d:
        so = Path(d) / "object-service-prelude.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_object_service_prelude_be1f0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_service_prelude_be1f0
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        value = Input()
        value.active[0][0] = 1
        value.record_halfword[0][0] = 0x0f
        value.active[1][2] = 1
        value.record_halfword[1][2] = 0x08
        value.active[1][3] = 1
        value.record_halfword[1][3] = 0x07
        value.status_48[:] = (0, 1)
        value.status_callback_result[:] = (0, 0xabcdef01)
        result = Result()
        fn(ctypes.byref(value), ctypes.byref(result))
        assert result.service_call_count == 4
        assert list(result.service_object[:4]) == [0, 0, 1, 1]
        assert list(result.service_index[:4]) == [0, 0, 2, 3]
        assert list(result.service_selector[:4]) == [7, 7, 7, 7]
        assert result.status_call_count == 1 and result.status_call_object[0] == 1
        assert list(result.status_publication) == [0, 0xabcdef01]
        print("PASS: 0xbe1f0 paired service prelude sequencing")


if __name__ == "__main__":
    main()
