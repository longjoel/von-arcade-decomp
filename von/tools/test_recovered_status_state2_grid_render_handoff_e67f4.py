#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("frame_record_stride", ctypes.c_uint32),
                ("rendered_row_count", ctypes.c_uint32),
                ("first_text_column", ctypes.c_uint32),
                ("text_column_stride", ctypes.c_uint32),
                ("renderer_target", ctypes.c_uint32),
                ("renderer_call_count", ctypes.c_uint32),
                ("frame_selector_offsets", ctypes.c_uint32 * 4),
                ("renderer_arg0", ctypes.c_uint32 * 4),
                ("renderer_arg1", ctypes.c_uint32 * 4),
                ("loop_target", ctypes.c_uint32),
                ("profile_dispatch_target", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-state2-render-handoff-") as d:
        so = Path(d) / "status-state2-render-handoff.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_state2_grid_render_handoff_e67f4.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_state2_grid_render_handoff_e67f4
        fn.restype = Result
        out = fn()
        assert (out.frame_record_stride, out.rendered_row_count,
                out.first_text_column, out.text_column_stride, out.renderer_target,
                out.renderer_call_count, list(out.frame_selector_offsets),
                list(out.renderer_arg0), list(out.renderer_arg1), out.loop_target,
                out.profile_dispatch_target, out.next_target) == \
            (12, 4, 19, 3, 0x1d880, 4, [0x40, 0x4c, 0x58, 0x64],
             [2, 31, 2, 31], [13, 16, 25, 28], 0xe6818, 0xe6500, 0xe6c50)
        print("PASS: 0xe67f4 state-2 grid render handoff")


if __name__ == "__main__":
    main()
