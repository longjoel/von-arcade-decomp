#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Entry(ctypes.Structure):
    _fields_ = [("column", ctypes.c_uint32), ("row", ctypes.c_uint32),
                ("string_address", ctypes.c_uint32), ("wrapper_variant", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("entry", Entry * 14), ("entry_count", ctypes.c_uint32),
                ("selected_value", ctypes.c_uint32), ("selected_shifted", ctypes.c_uint32),
                ("marker_clear_address", ctypes.c_uint32),
                ("marker_selected_address", ctypes.c_uint32),
                ("marker_clear_value", ctypes.c_uint32),
                ("marker_selected_value", ctypes.c_uint32),
                ("marker_mode_nonzero", ctypes.c_uint32), ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-diagnostic-menu-") as d:
        so = Path(d) / "diagnostic-menu.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_diagnostic_menu_render_eb060.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_diagnostic_menu_render_eb060
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        out = fn(3)
        assert out.entry_count == 14
        assert [(out.entry[i].column, out.entry[i].row, out.entry[i].string_address,
                 out.entry[i].wrapper_variant) for i in range(14)] == [
            (7, 23, 0xeaf40, 2), (13, 23, 0xeaf50, 0), (15, 23, 0xeaf60, 0),
            (17, 23, 0xeaf70, 0), (19, 23, 0xeaf80, 0), (21, 23, 0xeaf90, 0),
            (23, 23, 0xeafa0, 0), (25, 23, 0xeafb0, 0), (27, 23, 0xeafd0, 0),
            (29, 23, 0xeaff0, 0), (31, 23, 0xeb000, 0), (33, 23, 0xeb018, 0),
            (40, 19, 0xeb020, 0), (41, 21, 0xeb040, 0)]
        assert (out.selected_shifted, out.marker_clear_address,
                out.marker_selected_address, out.marker_clear_value,
                out.marker_selected_value, out.marker_mode_nonzero,
                out.return_target) == (0x300, 0x10048aa, 0x10049aa, 0, 30, 1, 0xeb19c)
        out = fn(0)
        assert (out.marker_clear_address, out.marker_selected_address,
                out.marker_mode_nonzero, out.return_target) == (0x10050aa, 0x10046aa, 0, 0xeb1b4)
        print("PASS: 0xeb060 diagnostic menu render plan")


if __name__ == "__main__":
    main()
