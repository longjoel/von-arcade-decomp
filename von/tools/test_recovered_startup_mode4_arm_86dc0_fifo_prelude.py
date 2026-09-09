#!/usr/bin/env python3
"""Validate slot-20 upload and FIFO prelude."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_86dc0_fifo_prelude.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "upload_call", "first_source", "first_destination", "first_bytes",
        "second_source", "second_destination", "second_bytes", "fifo_address",
        "fifo_word_count", "fifo_words0", "fifo_words1", "fifo_words2", "fifo_words3",
        "fifo_words4", "fifo_words5", "fifo_words6", "response_source_address",
        "fifo_write_address", "fifo_write_count", "response_compare_value",
        "response_value", "value_503ad8", "value_5040d8", "value_503ae0",
        "value_5040e0", "response_match", "response_dispatch_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prelude.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_86dc0_fifo_prelude
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(1, 0x11111111, 0x22222222, 0x33333333, 0x44444444,
                  ctypes.byref(result)) == 1
        assert (result.upload_call, result.first_source, result.first_destination,
                result.first_bytes) == (0xf5d40, 0x51c9e0, 0x503ad0, 0x600)
        assert (result.second_source, result.second_destination, result.second_bytes) == \
            (0x51cfe0, 0x5040d0, 0x600)
        assert result.fifo_address == 0x884000 and result.fifo_word_count == 7
        assert (result.response_source_address, result.fifo_write_address,
                result.fifo_write_count) == (0x51c9d0, 0x884000, 7)
        assert [result.fifo_words0, result.fifo_words1, result.fifo_words2,
                result.fifo_words3, result.fifo_words4, result.fifo_words5,
                result.fifo_words6] == [31, 0x11111111, 0x22222222, 0, 0,
                                       0x33333333, 0x44444444]
        assert (result.value_503ad8, result.value_5040d8,
                result.value_503ae0, result.value_5040e0) == (
                    0x11111111, 0x22222222, 0x33333333, 0x44444444)
        assert result.response_match == 1 and result.response_dispatch_target == 0x86eec

        result = Result()
        fn(0, 0, 0, 0, 0, ctypes.byref(result))
        assert result.response_match == 0 and result.response_dispatch_target == 0x873dc

    print("PASS: 0x86dc0 startup slot-20 FIFO prelude")


if __name__ == "__main__":
    main()
