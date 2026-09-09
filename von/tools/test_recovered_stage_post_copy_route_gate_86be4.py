"""Vectors for the 0x86be4 post-copy route gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_post_copy_route_gate_86be4.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_post_copy_route_gate_86be4.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("value_503a04", ctypes.c_uint32),
                        ("value_503ca2", ctypes.c_uint32),
                        ("value_5042a2", ctypes.c_uint32),
                        ("expected_503a04", ctypes.c_uint32),
                        ("route", ctypes.c_uint32),
                        ("target", ctypes.c_uint32)]

        function = loaded.recovered_stage_post_copy_route_gate_86be4
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86be4:.*ld.*0x503a04",
                        r"86bec:.*cmpibne.*0x86cb8",
                        r"86bf0:.*ldis.*0x503ca2",
                        r"86bf8:.*cmpibe.*0x86c08",
                        r"86bfc:.*ldis.*0x5042a2",
                        r"86c04:.*cmpibne.*0x86c64"):
        assert re.search(instruction, listing)

    with build() as function:
        assert (function(0x59, 1, 1).route,
                function(0x59, 1, 1).target) == (2, 0x86CB8)
        assert (function(0x5A, 0, 1).route,
                function(0x5A, 0, 1).target) == (0, 0x86C08)
        assert (function(0x5A, 1, 0).route,
                function(0x5A, 1, 0).target) == (0, 0x86C08)
        assert (function(0x5A, 1, 1).route,
                function(0x5A, 1, 1).target) == (1, 0x86C64)
        assert function(0x5A, 0xFFFFFFFF, 0xFFFFFFFF).target == 0x86C64
    print("recovered 0x86be4 post-copy-route vectors: ok")


if __name__ == "__main__":
    main()
