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
                ("status_504d24", ctypes.c_uint32),
                ("status_504d2e", ctypes.c_uint32),
                ("device_bit_address", ctypes.c_uint32),
                ("device_bit", ctypes.c_uint32),
                ("source_base", ctypes.c_uint32),
                ("source_stride", ctypes.c_uint32),
                ("source_count", ctypes.c_uint32),
                ("frame_record_stride", ctypes.c_uint32),
                ("first_rendered_row", ctypes.c_uint32),
                ("rendered_row_count", ctypes.c_uint32),
                ("first_frame_offset", ctypes.c_uint32),
                ("first_text_column", ctypes.c_uint32),
                ("text_column_stride", ctypes.c_uint32),
                ("renderer_target", ctypes.c_uint32),
                ("profile_dispatch_target", ctypes.c_uint32),
                ("profile_call_count", ctypes.c_uint32),
                ("frame_selector_offsets", ctypes.c_uint32 * 4),
                ("renderer_arg0", ctypes.c_uint32 * 4),
                ("renderer_arg1", ctypes.c_uint32 * 4),
                ("continuation", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-state2-second-half-") as d:
        so = Path(d) / "status-state2-second-half.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_service_state2_second_half_e6968.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_service_state2_second_half_e6968
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        out = fn(0x674)
        assert (out.route, out.status_504d2c, out.status_504d24,
                out.status_504d2e, out.device_bit_address, out.device_bit,
                out.source_base, out.source_stride, out.source_count,
                out.frame_record_stride, out.first_rendered_row,
                out.rendered_row_count, out.first_frame_offset,
                out.first_text_column, out.text_column_stride, out.renderer_target,
                out.profile_dispatch_target, out.profile_call_count,
                list(out.frame_selector_offsets), list(out.renderer_arg0),
                list(out.renderer_arg1), out.continuation) == \
            (1, 0xc000, 0x200, 0x8000, 0x100a000, 9, 0x1d000a4, 16, 10,
             12, 4, 4, 0x30, 19, 3, 0x1d880, 0xe6500, 4,
             [0x70, 0x7c, 0x88, 0x94], [2, 31, 2, 31], [13, 16, 25, 28],
             0xe6c50)
        assert fn(0x675).route == 0
        print("PASS: 0xe6968 state-2 remainder-0x674 second half")


if __name__ == "__main__":
    main()
