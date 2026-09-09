#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Plan(ctypes.Structure):
    _fields_ = [("callee", ctypes.c_uint32),
                ("object_subtable", ctypes.c_uint32),
                ("context_base", ctypes.c_uint32),
                ("special_object", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-dispatch-context-") as d:
        so = Path(d) / "object-dispatch-context.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_object_dispatch_context_bf180.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_dispatch_context_bf180
        fn.argtypes = [ctypes.c_int, ctypes.c_uint32, ctypes.POINTER(Plan)]
        result = Plan()
        assert fn(0, 0x503ad0, ctypes.byref(result)) == 1
        assert (result.callee, result.object_subtable, result.context_base,
                result.special_object) == (0xa1050, 0x503cd0, 0x565320, 1)
        assert fn(1, 0x5040d0, ctypes.byref(result)) == 1
        assert (result.callee, result.object_subtable, result.context_base,
                result.special_object) == (0xa98f0, 0x5042d0, 0x5658a0, 0)
        assert fn(2, 0x503ad0, ctypes.byref(result)) == 1 and result.callee == 0xa55e0
        assert fn(3, 0, ctypes.byref(result)) == 0
        print("PASS: shared object dispatch context routing")


if __name__ == "__main__":
    main()
