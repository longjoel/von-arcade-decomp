"""Vectors for the bounded 0x85d04 callback table-row adjustment."""

import ctypes
import pathlib
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_table_row_adjust_85d04.c"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_table_row_adjust_85d04.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))
        class Result(ctypes.Structure):
            _fields_ = [("state", ctypes.c_uint32),
                        ("selector", ctypes.c_uint32),
                        ("row_offset", ctypes.c_uint32),
                        ("current_before", ctypes.c_int32),
                        ("current_after", ctypes.c_int32),
                        ("paired_before", ctypes.c_int32),
                        ("paired_after", ctypes.c_int32),
                        ("paired_capped", ctypes.c_uint32),
                        ("exits_without_pair_write", ctypes.c_uint32)]
        function = loaded.recovered_scheduler_callback_table_row_adjust_85d04
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_int32, ctypes.c_int32]
        function.restype = Result
        yield function


def main():
    with build() as function:
        result = function(2, 3, 70, 1000)
        assert result.row_offset == 2 * 1152 + 3 * 144 + 0x8E
        assert result.current_after == 100
        assert result.paired_after == 1000
        assert result.exits_without_pair_write == 1

        result = function(7, 0xF, -20, 1001)
        assert result.row_offset == 7 * 1152 + 0xF * 144 + 0x8E
        assert result.current_after == 10
        assert result.paired_after == 1000
        assert result.paired_capped == 1
    print("recovered 0x85d04 table-row vectors: ok")


if __name__ == "__main__":
    main()
