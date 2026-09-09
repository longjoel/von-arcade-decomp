#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("variant", ctypes.c_uint32), ("input_value_g2", ctypes.c_uint32),
        ("helper_input_r4", ctypes.c_uint32), ("helper_output_r4", ctypes.c_uint32),
        ("pre_adjusted_g0", ctypes.c_uint32), ("board_byte", ctypes.c_uint32),
        ("selected_board_argument", ctypes.c_uint32), ("board_helper_address", ctypes.c_uint32),
        ("final_argument_g0", ctypes.c_uint32), ("numeric_helper_address", ctypes.c_uint32),
        ("final_helper_address", ctypes.c_uint32), ("return_address", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-runtime-format-") as d:
        so = Path(d) / "runtime-format.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_format_wrappers_eaeb0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_format_wrappers_eaeb0
        fn.argtypes = [ctypes.c_uint32] * 5
        fn.restype = Result
        out = fn(0, 0x1234, 0x5678, 9, 0)
        assert (out.helper_input_r4, out.final_argument_g0, out.numeric_helper_address,
                out.final_helper_address, out.return_address) == (0x1234, 0x5678, 0x1cac8, 0xf5100, 0xeaec0)
        for board, argument in ((1, 32), (2, 32), (0xff, 42)):
            out = fn(1, 0x1234, 0x5678, 9, board)
            assert (out.pre_adjusted_g0, out.board_byte, out.selected_board_argument,
                    out.board_helper_address, out.final_argument_g0, out.return_address) == (
                8, board & 0xff, argument, 0x1cc40, 0x5678, 0xeaf1c)
        out = fn(2, 0x1234, 0x5678, 9, 0)
        assert (out.numeric_helper_address, out.final_helper_address, out.return_address) == (0x1cac8, 0x1da90, 0xeaf30)
        print("PASS: 0xeaeb0/0xeaed0/0xeaf20 format wrappers")


if __name__ == "__main__":
    main()
