"""Vectors for the 0x865e0 stage-mode publication stores."""

import ctypes
import pathlib
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_mode_publication_865e0.c"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_mode_publication_865e0.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))
        class Result(ctypes.Structure):
            _fields_ = [("previous_words", ctypes.c_uint32 * 4),
                        ("previous_pair", ctypes.c_uint32 * 2),
                        ("current_words", ctypes.c_uint32 * 4),
                        ("current_pair", ctypes.c_uint32 * 2),
                        ("active_words", ctypes.c_uint32 * 4),
                        ("active_pair", ctypes.c_uint32 * 2),
                        ("latch_509b80", ctypes.c_uint32),
                        ("latch_509b84", ctypes.c_uint32),
                        ("latch_509b88", ctypes.c_uint32)]
        function = loaded.recovered_stage_mode_publication_865e0
        function.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                             ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    with build() as function:
        words = (ctypes.c_uint32 * 4)(1, 2, 3, 4)
        pair = (ctypes.c_uint32 * 2)(5, 6)
        result = function(words, pair, 0xABCD)
        assert list(result.previous_words) == [1, 2, 3, 4]
        assert list(result.current_words) == [1, 2, 3, 4]
        assert list(result.active_pair) == [5, 6]
        assert result.latch_509b80 == 0xABCD
        assert result.latch_509b84 == 0xABCD
        assert result.latch_509b88 == 0xABCD
    print("recovered 0x865e0 publication vectors: ok")


if __name__ == "__main__":
    main()
