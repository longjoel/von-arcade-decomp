"""Vectors for the 0x85c88 callback byte-map candidate scan."""

import ctypes
import pathlib
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_byte_map_scan_85c88.c"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_byte_map_scan_85c88.c"\n'
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
                        ("used_primary_gate", ctypes.c_uint32),
                        ("used_fallback_gate", ctypes.c_uint32),
                        ("row_adjust_path", ctypes.c_uint32),
                        ("rejected", ctypes.c_uint32),
                        ("map_after", ctypes.c_uint8 * 32)]
        function = loaded.recovered_scheduler_callback_byte_map_scan_85c88
        function.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.c_uint8, ctypes.c_uint8]
        function.restype = Result
        yield function


def main():
    with build() as function:
        values = (ctypes.c_uint8 * 32)(*[0] * 32)
        values[4] = 0xB3
        values[9] = 0x03
        result = function(values, 1 << 10, 7, 0, 0x20)
        assert result.rejected == 1

        values = (ctypes.c_uint8 * 32)(*[0] * 32)
        values[4] = 0xB3
        values[9] = 0x04
        result = function(values, 0, 0, 1, 0x21)
        assert result.candidate_index == 4
        assert result.candidate_nibble == 3
        assert result.used_fallback_gate == 1
        assert result.row_adjust_path == 1
        assert result.map_after[4] == 0x21

        values = (ctypes.c_uint8 * 32)(*[0] * 32)
        values[2] = 0x81
        values[7] = 0x02
        result = function(values, 1 << 10, 9, 1, 0x20)
        assert result.candidate_index == 2
        assert result.used_primary_gate == 1
        assert result.candidate_nibble == 1

        values = (ctypes.c_uint8 * 32)(*[0] * 32)
        values[2] = 0x81
        values[3] = 0x01
        result = function(values, 0, 0, 0, 0x20)
        assert result.rejected == 1
    print("recovered 0x85c88 byte-map vectors: ok")


if __name__ == "__main__":
    main()
