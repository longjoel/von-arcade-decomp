"""Vectors for the 0x86174 secondary byte-map finalizer."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_secondary_byte_map_finalize_86174.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_secondary_byte_map_finalize_86174.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))
        class Result(ctypes.Structure):
            _fields_ = [("writes", ctypes.c_uint32),
                        ("map_after", ctypes.c_uint8 * 32)]
        function = loaded.recovered_scheduler_callback_secondary_byte_map_finalize_86174
        function.argtypes = [ctypes.POINTER(ctypes.c_uint8),
                             ctypes.POINTER(ctypes.c_uint16),
                             ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"861a8:.*ldob.*\(r6\)",
                        r"861b0:.*setbit.*6,g4,g4",
                        r"861b4:.*stob.*0x1\(g7\)\[g3\]"):
        assert re.search(instruction, listing)

    with build() as function:
        object_bytes = (ctypes.c_uint8 * 32)(*[1] * 32)
        object_words = (ctypes.c_uint16 * 32)(*[1] * 32)
        byte_map = (ctypes.c_uint8 * 32)(*[0] * 32)
        byte_map[8] = 0x44
        result = function(object_bytes, object_words, byte_map,
                          (1 << 11) | 0x0B)
        assert result.writes == 31
        assert result.map_after[0] == 0x4B
        assert result.map_after[8] == 0x44

        object_bytes[2] = 0
        object_words[3] = 0
        result = function(object_bytes, object_words, byte_map, 0x0B)
        assert result.writes == 0
        result = function(object_bytes, object_words, byte_map,
                          (1 << 11) | 0x0B)
        assert result.map_after[2] == 0
        assert result.map_after[3] == 0
    print("recovered 0x86174 secondary-map vectors: ok")


if __name__ == "__main__":
    main()
