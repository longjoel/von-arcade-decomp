"""Vectors for the 0x86b98 post-copy stage tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_post_copy_tail_86b98.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_post_copy_tail_86b98.c"\n'
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
                        ("targets", ctypes.c_uint32 * 6),
                        ("source_halfword", ctypes.c_uint32 * 2),
                        ("destination_halfword", ctypes.c_uint32 * 2),
                        ("call_23d60_g0", ctypes.c_uint32),
                        ("call_71080_g0", ctypes.c_uint32),
                        ("continuation", ctypes.c_uint32)]

        function = loaded.recovered_stage_post_copy_tail_86b98
        function.argtypes = []
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86b98:.*lda.*0x503ad0",
                        r"86bb0:.*ldos.*0x51cbb0",
                        r"86bb8:.*ldos.*0x51d1b0",
                        r"86bc0:.*mov.*1,g0",
                        r"86bd4:.*call.*0x23d60",
                        r"86be0:.*call.*0x71080"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function()
        assert result.call_count == 6
        assert list(result.targets) == [0xBECE0, 0x9B320, 0x41F20,
                                        0xC5530, 0x23D60, 0x71080]
        assert list(result.source_halfword) == [0x51CBB0, 0x51D1B0]
        assert list(result.destination_halfword) == [0x503CA0, 0x5042A0]
        assert result.call_23d60_g0 == 1
        assert result.call_71080_g0 == 0x503AD0
        assert result.continuation == 0x86BE4
    print("recovered 0x86b98 post-copy-tail vectors: ok")


if __name__ == "__main__":
    main()
