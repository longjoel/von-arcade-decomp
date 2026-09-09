"""Vectors for the bounded 0x860d4 secondary fallback mutation."""

import ctypes
import pathlib
import subprocess
import re
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_secondary_fallback_mutation_860d4.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


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
                        ("matching_entries", ctypes.c_uint32),
                        ("map_replaced", ctypes.c_uint32),
                        ("map_after", ctypes.c_uint8 * 32)]
        function = loaded.recovered_scheduler_callback_secondary_fallback_mutation_860d4
        function.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
                             ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_int32, ctypes.c_int32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"860d4:.*and.*g5,15,g4", r"8612c:.*cmpobg.*0x8614c",
                        r"86150:.*ldob.*0x1\(g3\)\[g5\*2\]",
                        r"86164:.*stob.*g14,0x1\(g7\)\[g3\]"):
        assert re.search(instruction, listing)

    with build() as function:
        values = (ctypes.c_uint8 * 32)(*[0] * 32)
        values[5] = 0xD7
        values[9] = 0x17
        result = function(values, 5, 0x21, 4, 2, 100, 49)
        assert result.candidate_nibble == 7
        assert result.row_offset == 4 * 1088 + 2 * 136 + 0x86
        assert result.current_after == 90
        assert result.paired_after == 40
        assert result.map_after[5] == 0x21
        assert result.matching_entries == 2
        assert result.map_replaced == 1

        result = function(values, 5, 0x21, 4, 2, 100, 50)
        assert result.paired_after == 50
        assert result.map_replaced == 1

    print("recovered 0x860d4 fallback-mutation vectors: ok")


if __name__ == "__main__":
    main()
