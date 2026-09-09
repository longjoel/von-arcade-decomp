#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("remainder", ctypes.c_uint32),
                ("route", ctypes.c_uint32),
                ("status_504d2c", ctypes.c_uint32),
                ("status_504d2e", ctypes.c_uint32),
                ("status_504d24", ctypes.c_uint32),
                ("device_bit_address", ctypes.c_uint32),
                ("device_bit", ctypes.c_uint32),
                ("renderer_arg0", ctypes.c_uint32),
                ("renderer_arg1", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32),
                ("record_base", ctypes.c_uint32),
                ("first_record_offset", ctypes.c_uint32),
                ("record_index_offset", ctypes.c_uint32),
                ("record_stride", ctypes.c_uint32),
                ("record_count", ctypes.c_uint32),
                ("first_text_column", ctypes.c_uint32),
                ("text_column_stride", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-variant-654-") as d:
        so = Path(d) / "status-variant-654.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_transition_variant_654_prefix_e62f8.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_transition_variant_654_prefix_e62f8
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result

        fallthrough = fn(0x655)
        assert (fallthrough.route, fallthrough.continuation) == (0, 0xe6410)

        render = fn(0x654)
        assert (render.route, render.status_504d2c, render.status_504d2e,
                render.status_504d24, render.device_bit_address, render.device_bit,
                render.renderer_arg0, render.renderer_arg1, render.helper_target,
                render.record_base, render.first_record_offset,
                render.record_index_offset, render.record_stride, render.record_count,
                render.first_text_column, render.text_column_stride,
                render.continuation) == \
            (1, 0xc000, 0x8000, 0x200, 0x100a000, 9, 13, 12, 0x1cac8,
             0x578460, 0x3c, 31, 12, 5, 19, 3, 0xe6410)
        print("PASS: 0xe62f8 state-1 remainder-0x654 renderer prefix")


if __name__ == "__main__":
    main()
