"""Vectors for the 0x869d0 stage callback dispatch plan."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_callback_dispatch_869d0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_callback_dispatch_869d0.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("saved_input", ctypes.c_uint32),
                        ("frame_builder_target", ctypes.c_uint32),
                        ("helper_argument0", ctypes.c_uint32),
                        ("helper_argument1", ctypes.c_uint32),
                        ("helper_target", ctypes.c_uint32),
                        ("selector", ctypes.c_uint32),
                        ("descriptor", ctypes.c_uint32),
                        ("target", ctypes.c_uint32),
                        ("returns", ctypes.c_uint32)]

        function = loaded.recovered_stage_callback_dispatch_869d0
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"869d0:.*mov.*g0,r4",
                        r"869d4:.*call.*0x85b00",
                        r"869dc:.*mov.*r4,g1",
                        r"869ec:.*cmpobl.*6",
                        r"869f0:.*ld.*0x869fc\[g4\*4\]"):
        assert re.search(instruction, listing)

    with build() as function:
        for selector, descriptor, target in (
                (0, 0x000869C8, 0x1D7D0),
                (1, 0x000869CA, 0x1D9E0),
                (2, 0x000869C8, 0x1D9E0),
                (3, 0x000869CA, 0x1D880),
                (4, 0x000869C8, 0x1D880),
                (5, 0x000869CA, 0x1D930),
                (6, 0x000869C8, 0x1D930)):
            result = function(0x1234, selector)
            assert result.saved_input == 0x1234
            assert result.frame_builder_target == 0x85B00
            assert (result.helper_argument0, result.helper_argument1) == (10, 0x1234)
            assert result.helper_target == 0x1CAC8
            assert (result.descriptor, result.target) == (descriptor, target)
            assert result.returns == 0
        result = function(0x1234, 7)
        assert result.returns == 1
        assert result.target == 0
    print("recovered 0x869d0 callback-dispatch vectors: ok")


if __name__ == "__main__":
    main()
