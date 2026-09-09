"""Vectors for the 0x86c08 publication mapper."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_publication_map_86c08.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_publication_map_86c08.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("entry", ctypes.c_uint32),
                        ("value_503aa4", ctypes.c_int32),
                        ("publication_51c9a4", ctypes.c_uint32),
                        ("publication_51c9ac", ctypes.c_uint32),
                        ("publication_address_1", ctypes.c_uint32),
                        ("publication_address_2", ctypes.c_uint32),
                        ("continuation", ctypes.c_uint32)]

        function = loaded.recovered_stage_publication_map_86c08
        function.argtypes = [ctypes.c_uint32, ctypes.c_int32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86c08:.*ld.*0x503a7c",
                        r"86c20:.*ld.*0x503aa4",
                        r"86c44:.*st.*0x51c9a4",
                        r"86c50:.*0x86cb0",
                        r"86c64:.*ld.*0x503aa4",
                        r"86cb0:.*st.*0x51c9ac"):
        assert re.search(instruction, listing)

    with build() as function:
        expected = {
            0: (12, 1), 1: (19, 0xB4), 2: (12, 0xB4),
            3: (19, 0xB4), -1: (19, 0xB4)
        }
        for value, pair in expected.items():
            result = function(0, value)
            assert (result.publication_51c9a4, result.publication_51c9ac) == pair

        assert (function(1, 0).publication_51c9a4,
                function(1, 0).publication_51c9ac) == (12, 1)
        assert (function(1, 1).publication_51c9a4,
                function(1, 1).publication_51c9ac) == (12, 1)
        assert (function(1, 2).publication_51c9a4,
                function(1, 2).publication_51c9ac) == (12, 0xB4)
        result = function(1, -1)
        assert (result.publication_51c9a4, result.publication_51c9ac) == (12, 0xB4)
        assert (result.publication_address_1, result.publication_address_2,
                result.continuation) == (0x51C9A4, 0x51C9AC, 0x86CB8)
    print("recovered 0x86c08 publication-map vectors: ok")


if __name__ == "__main__":
    main()
