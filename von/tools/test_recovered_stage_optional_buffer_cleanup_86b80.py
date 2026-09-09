"""Vectors for the 0x86b80 optional stage-buffer cleanup gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_optional_buffer_cleanup_86b80.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_optional_buffer_cleanup_86b80.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("control_value", ctypes.c_uint32),
                        ("calls_cleanup", ctypes.c_uint32),
                        ("target", ctypes.c_uint32),
                        ("argument", ctypes.c_uint32),
                        ("continuation", ctypes.c_uint32)]

        function = loaded.recovered_stage_optional_buffer_cleanup_86b80
        function.argtypes = [ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86b80:.*ld.*0x503a7c",
                        r"86b88:.*cmpibne.*0x86b98",
                        r"86b94:.*call.*0xdf070"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(0)
        assert result.calls_cleanup == 1
        assert (result.target, result.argument, result.continuation) == (
            0xDF070, 0x5040D0, 0x86B98)
        result = function(1)
        assert result.calls_cleanup == 0
    print("recovered 0x86b80 optional-cleanup vectors: ok")


if __name__ == "__main__":
    main()
