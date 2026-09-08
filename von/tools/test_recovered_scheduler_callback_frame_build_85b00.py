"""Vectors for the bounded 0x85b00 callback-frame builder."""

import ctypes
import pathlib
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_frame_build_85b00.c"


@contextmanager
def build():
    wrapper = r'''
#include <stdint.h>
#include "recovered_scheduler_callback_frame_build_85b00.c"
'''
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))
        class Result(ctypes.Structure):
            _fields_ = [("frame", ctypes.c_int32 * 6),
                        ("scaled_r7", ctypes.c_int32),
                        ("scaled_r5", ctypes.c_int32),
                        ("scaled_g7", ctypes.c_int32),
                        ("frame_slot_40", ctypes.c_int32),
                        ("frame_slot_44", ctypes.c_int32),
                        ("frame_slot_48", ctypes.c_int32),
                        ("frame_slot_4c", ctypes.c_int32),
                        ("frame_slot_50", ctypes.c_int32),
                        ("frame_slot_54", ctypes.c_int32),
                        ("lowest_value", ctypes.c_int32),
                        ("third_value", ctypes.c_int32),
                        ("lowest_index", ctypes.c_uint32),
                        ("selected_504e48", ctypes.c_uint32),
                        ("return_stub", ctypes.c_uint32)]
        function = loaded.recovered_scheduler_callback_frame_build_85b00
        function.argtypes = [ctypes.POINTER(ctypes.c_int32)]
        function.restype = Result
        yield function


def main():
    with build() as function:
        values = (ctypes.c_int32 * 6)(-10, 4, 8, 12, 20, 30)
        result = function(values)
        assert result.scaled_r7 == 20
        assert result.scaled_r5 == 6
        assert result.scaled_g7 == 50
        assert result.frame_slot_4c == 25
        assert result.lowest_value == -10
        assert result.lowest_index == 0
        assert result.selected_504e48 == 0
        assert result.return_stub == 0x85BEC

        values = (ctypes.c_int32 * 6)(-600, -100, 0, 100, 200, 300)
        result = function(values)
        assert result.lowest_value == -600
        assert result.third_value == 0
        assert result.selected_504e48 == 6

        values = (ctypes.c_int32 * 6)(1, 2, 3, 4, 5, 6)
        result = function(values)
        assert result.lowest_index == 6
        assert result.selected_504e48 == 6
    print("recovered 0x85b00 callback-frame vectors: ok")


if __name__ == "__main__":
    main()
