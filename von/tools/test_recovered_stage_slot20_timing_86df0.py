"""Vectors for the slot-20 timing normalization."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_slot20_timing_86df0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_slot20_timing_86df0.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("slot_index", ctypes.c_uint32),
                        ("marker", ctypes.c_uint32),
                        ("remainder", ctypes.c_uint32),
                        ("bucket_candidate", ctypes.c_uint32),
                        ("published_state", ctypes.c_uint32),
                        ("published_timing", ctypes.c_uint32),
                        ("state_address", ctypes.c_uint32),
                        ("timing_address", ctypes.c_uint32),
                        ("modulus", ctypes.c_uint32),
                        ("group_shift", ctypes.c_uint32),
                        ("continuation", ctypes.c_uint32)]

        function = loaded.recovered_stage_slot20_timing_86df0
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86df0:.*ld.*0x51c9b0",
                        r"86dfc:.*cmpobg.*0x86e14",
                        r"86e18:.*remo",
                        r"86e1c:.*shro.*2",
                        r"86e20:.*lda.*\[g4\*4\]",
                        r"86e60:.*cmpible.*0x86e74"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(17, 0x5A)
        assert (result.remainder, result.bucket_candidate,
                result.published_state, result.published_timing) == (17, 0, 0x5A, 17)
        result = function(119, 0x5A)
        assert result.published_state == 0x5A
        result = function(120, 0x5A)
        assert (result.remainder, result.bucket_candidate,
                result.published_state, result.published_timing) == (0, 4, 4, 0)
        result = function(359, 0x5A)
        assert (result.remainder, result.bucket_candidate,
                result.published_state, result.published_timing) == (119, 120, 0x5A, 119)
        assert (result.state_address, result.timing_address,
                result.modulus, result.group_shift, result.continuation) == (
            0x51D5E4, 0x51D5E8, 120, 2, 0x86E74)
    print("recovered 0x86df0 slot20-timing vectors: ok")


if __name__ == "__main__":
    main()
