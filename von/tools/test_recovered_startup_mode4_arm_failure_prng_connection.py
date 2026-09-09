#!/usr/bin/env python3
"""Validate the 0xf5058 -> 0x878e8 slot-20 connection."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "von/i960/recovered_runtime_math.c"
BRIDGE = ROOT / "von/i960/recovered_startup_mode4_arm_878e8_failure_bridge.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_call", "helper_result", "mask", "stored_address", "stored_value",
        "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "connection.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(RUNTIME), str(BRIDGE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))
        step = recovered.recovered_random_step
        step.argtypes = [ctypes.c_uint32]
        step.restype = ctypes.c_uint32
        bridge = recovered.recovered_startup_mode4_arm_878e8_failure_bridge
        bridge.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        bridge.restype = ctypes.c_int
        for state in (0, 1, 2, 0x01234567, 0x40000000, 0x7fffffff, 0xffffffff):
            helper_result = step(state)
            result = Result()
            assert bridge(helper_result, ctypes.byref(result)) == 1
            assert result.helper_call == 0xf5058 and result.helper_result == helper_result
            assert result.mask == 1 and result.stored_address == 0x51c97c
            assert result.stored_value == helper_result & 1
            assert result.continuation_target == 0x878f8
    print("PASS: 0xf5058 to 0x878e8 PRNG connection")


if __name__ == "__main__":
    main()
