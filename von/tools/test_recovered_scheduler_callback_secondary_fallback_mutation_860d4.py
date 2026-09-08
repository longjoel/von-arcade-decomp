"""Vectors for the bounded 0x860d4 secondary fallback mutation."""

import ctypes
import pathlib
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_secondary_fallback_mutation_860d4.c"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_secondary_fallback_mutation_860d4.c"\n'
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
                        ("map_replaced", ctypes.c_uint32),
                        ("map_after", ctypes.c_uint8 * 32)]
        function = loaded.recovered_scheduler_callback_secondary_fallback_mutation_860d4
        function.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
                             ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_int32, ctypes.c_int32]
        function.restype = Result
        yield function


def main():
    with build() as function:
        values = (ctypes.c_uint8 * 32)(*[0] * 32)
        values[5] = 0xD7
        result = function(values, 5, 0x21, 4, 2, 100, 49)
        assert result.candidate_nibble == 7
        assert result.row_offset == 4 * 1088 + 2 * 136 + 0x86
        assert result.current_after == 90
        assert result.paired_after == 40
        assert result.map_after[5] == 0x21

        result = function(values, 5, 0x21, 4, 2, 100, 50)
        assert result.paired_after == 50
        assert result.map_replaced == 1
    print("recovered 0x860d4 fallback-mutation vectors: ok")


if __name__ == "__main__":
    main()
