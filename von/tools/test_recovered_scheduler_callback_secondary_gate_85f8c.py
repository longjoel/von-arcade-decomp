"""Vectors for the 0x85f8c secondary callback-map routing gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_secondary_gate_85f8c.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_secondary_gate_85f8c.c"\n'
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
                        ("route", ctypes.c_uint32),
                        ("map_bit6", ctypes.c_uint32),
                        ("previous_special_bits", ctypes.c_uint32),
                        ("current_is_zero", ctypes.c_uint32),
                        ("object_byte_is_zero", ctypes.c_uint32)]
        function = loaded.recovered_scheduler_callback_secondary_gate_85f8c
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint8,
                             ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint8]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"85f8c:.*ldob.*0x1\(g7\)\[g3\]",
                        r"85fa0:.*cmpibe.*0x860a0",
                        r"85ff0:.*cmpibe.*0x86000"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(7, 0, 0, 1, 1)
        assert result.route == 0
        result = function(7, 0x40, 0, 1, 1)
        assert result.candidate_index == 7
        assert result.route == 2

        result = function(7, 0x40, 1 << 9, 1, 1)
        assert result.route == 1
        result = function(7, 0x40, 0, 0, 1)
        assert result.route == 1
        result = function(7, 0x40, 0, 1, 0)
        assert result.route == 1
    print("recovered 0x85f8c secondary-gate vectors: ok")


if __name__ == "__main__":
    main()
