"""Vectors for the 0x86b0c post-copy service sequence."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_post_copy_services_86b0c.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_post_copy_services_86b0c.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("call_count", ctypes.c_uint32),
                        ("targets", ctypes.c_uint32 * 9),
                        ("buffer_arguments", ctypes.c_uint32 * 9),
                        ("dynamic_target_503ad4", ctypes.c_uint32),
                        ("dynamic_target_5040d4", ctypes.c_uint32),
                        ("continuation", ctypes.c_uint32)]

        function = loaded.recovered_stage_post_copy_services_86b0c
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86b0c:.*call.*0xde990",
                        r"86b18:.*call.*0xbe1f0",
                        r"86b38:.*callx.*\(g1\)",
                        r"86b5c:.*bal.*0x26cb8",
                        r"86b7c:.*callx.*\(g1\)"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(0x11111111, 0x22222222)
        assert result.call_count == 9
        assert list(result.targets) == [0xDE990, 0xBE1F0, 0xBD730,
                                        0x11111111, 0x23980, 0xDF070,
                                        0x26CB8, 0xBD810, 0x22222222]
        assert list(result.buffer_arguments) == [0xFFFFFFFF, 0x503AD0, 0x503AD0,
                                                 0x503AD0, 0x503AD0,
                                                 0x503AD0, 0x5040D0,
                                                 0x5040D0, 0x5040D0]
        assert result.continuation == 0x86B80
    print("recovered 0x86b0c post-copy-service vectors: ok")


if __name__ == "__main__":
    main()
