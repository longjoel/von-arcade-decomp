#!/usr/bin/env python3
"""Validate the slot-20 response FIFO builder prefix."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_88380_fifo_response_builder.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "setup_call", "setup_argument", "setup_seed", "endpoint_a0", "endpoint_a1",
        "endpoint_b0", "endpoint_b1", "delta_a", "delta_b", "packet10_0",
        "packet10_1", "packet10_2", "packet31_0", "packet31_1", "packet31_2",
        "packet31_3", "packet31_4", "packet31_5", "packet31_6", "fifo_address")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "builder.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_88380_fifo_response_builder
        fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        result = Result()
        assert fn(0x100, 0x80, 0x240, 0x200, ctypes.byref(result)) == 1
        assert result.setup_call == 0x2a990 and result.setup_argument == 0xd000
        assert result.setup_seed == 0 and result.delta_a == 0x140 and result.delta_b == 0x180
        assert (result.packet10_0, result.packet10_1, result.packet10_2) == (10, 0x180, 0x140)
        assert (result.packet31_0, result.packet31_1, result.packet31_2, result.packet31_3,
                result.packet31_4, result.packet31_5, result.packet31_6) == (
                    31, 0x100, 0x240, 0, 0, 0x80, 0x200)
        assert result.fifo_address == 0x884000

        result = Result()
        assert fn(0x240, 0x200, 0x100, 0x080, ctypes.byref(result)) == 1
        assert result.delta_a == 0xfffffec0 and result.delta_b == 0xfffffe80
        assert result.packet10_1 == 0xfffffe80 and result.packet10_2 == 0xfffffec0
    print("PASS: 0x88380 slot-20 FIFO response builder")


if __name__ == "__main__":
    main()
