#!/usr/bin/env python3
"""Validate the bounded response-helper gate at 0x8ca80."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_8ca80_response_gate.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "buffer", "threshold_address", "threshold_value", "source_value",
        "gate_address", "gate_value", "returned", "packet_path", "packet_entry")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8ca80_response_gate
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for buffer in (0x503ad0, 0x5040d0):
            for source, gate in ((0x76, 0), (0x77, 0), (0x78, 1), (0xffffffff, 1)):
                result = Result()
                assert fn(buffer, source, ctypes.byref(result)) == 1
                assert result.buffer == buffer
                assert (result.threshold_address, result.threshold_value) == (0x51c984, 0x77)
                assert result.source_value == source
                assert (result.gate_address, result.gate_value) == (0x51c99c, gate)
                assert result.returned == (1 if not gate else 0)
                assert result.packet_path == gate and result.packet_entry == 0x8ccfc
    print("PASS: 0x8ca80 response-helper gate")


if __name__ == "__main__":
    main()
