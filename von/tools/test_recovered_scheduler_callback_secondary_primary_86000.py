"""Vectors for the bounded 0x86000 primary secondary-map mutation."""

import ctypes
import pathlib
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_secondary_primary_86000.c"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_secondary_primary_86000.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))
        class Result(ctypes.Structure):
            _fields_ = [("candidate_index", ctypes.c_uint32),
                        ("candidate_nibble", ctypes.c_uint32),
                        ("row_offset", ctypes.c_uint32),
                        ("current_before", ctypes.c_int32),
                        ("current_after", ctypes.c_int32),
                        ("paired_before", ctypes.c_int32),
                        ("paired_after", ctypes.c_int32),
                        ("collision", ctypes.c_uint32),
                        ("exits_without_pair_write", ctypes.c_uint32)]
        function = loaded.recovered_scheduler_callback_secondary_primary_86000
        function.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
                             ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_int32, ctypes.c_int32]
        function.restype = Result
        yield function


def main():
    with build() as function:
        values = (ctypes.c_uint8 * 32)(*[0] * 32)
        values[4] = 0xB3
        values[9] = 0x03
        result = function(values, 4, 0x21, 2, 3, 70, 1001)
        assert result.collision == 1
        assert result.row_offset == 2 * 1088 + 3 * 136 + 0x86

        values = (ctypes.c_uint8 * 32)(*[0] * 32)
        values[4] = 0xB3
        result = function(values, 4, 0x21, 2, 3, 70, 1001)
        assert result.collision == 0
        assert result.current_after == 100
        assert result.paired_after == 1000

        result = function(values, 4, 0x21, 2, 3, 70, 1000)
        assert result.paired_after == 1000
        assert result.exits_without_pair_write == 1
    print("recovered 0x86000 secondary-primary vectors: ok")


if __name__ == "__main__":
    main()
