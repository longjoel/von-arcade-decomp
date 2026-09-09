#!/usr/bin/env python3
"""Validate the compact 0x8d0b0 callback/state trampolines."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_8d0b0_callback_trampolines.c"


class StoreResult(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("callback", "callback_return", "state_address", "state_value")]


class QueryResult(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("callback", "callback_return", "state_address", "state_value", "returned_value")]


class InitResult(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("callback", "callback_return", "timing_address", "timing_value", "progress_address", "progress_value", "latch_address", "latch_value")]


class Query140Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("callback", "callback_return", "state_address", "state_value", "returned_value")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "trampolines.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        store = lib.recovered_startup_mode4_arm_8d0b0_store
        store.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(StoreResult)]
        store.restype = ctypes.c_int
        out = StoreResult()
        assert store(0x1234, 7, ctypes.byref(out)) == 1
        assert (out.callback, out.callback_return, out.state_address, out.state_value) == (0x1234, 0x8d0cc, 0x51c9d0, 7)

        query = lib.recovered_startup_mode4_arm_8d0d0_query
        query.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(QueryResult)]
        query.restype = ctypes.c_int
        for state, value in ((0, 0), (1, 1), (2, 0)):
            out = QueryResult()
            assert query(0x5678, state, ctypes.byref(out)) == 1
            assert (out.callback_return, out.state_address, out.state_value, out.returned_value) == (0x8d0fc, 0x51d5e0, state, value)

        initialize = lib.recovered_startup_mode4_arm_8d100_initialize
        initialize.argtypes = [ctypes.c_uint32, ctypes.POINTER(InitResult)]
        initialize.restype = ctypes.c_int
        out = InitResult()
        assert initialize(0x9abc, ctypes.byref(out)) == 1
        assert (out.callback, out.callback_return) == (0x9abc, 0x8d134)
        assert (out.timing_address, out.timing_value) == (0x51d5e0, 2)
        assert (out.progress_address, out.progress_value) == (0x503a04, 1)
        assert (out.latch_address, out.latch_value) == (0x51c9c0, 1)

        query140 = lib.recovered_startup_mode4_arm_8d140_query
        query140.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Query140Result)]
        query140.restype = ctypes.c_int
        for state, value in ((0, 0), (1, 1), (2, 0)):
            out = Query140Result()
            assert query140(0xabcd, state, ctypes.byref(out)) == 1
            assert (out.callback, out.callback_return, out.state_address,
                    out.state_value, out.returned_value) == (0xabcd, 0x8d16c, 0x51c9c0, state, value)
    print("PASS: 0x8d0b0 callback trampolines")


if __name__ == "__main__":
    main()
