"""Vectors for the 0x86a90 stage service prologue."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_service_prologue_86a90.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_service_prologue_86a90.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("marker_503a60", ctypes.c_uint32),
                        ("halfword_504b94", ctypes.c_uint16),
                        ("call_count", ctypes.c_uint32),
                        ("call_targets", ctypes.c_uint32 * 6),
                        ("zero_argument_call_indices", ctypes.c_uint32 * 2),
                        ("falls_through_to_86ac0", ctypes.c_uint32)]

        function = loaded.recovered_stage_service_prologue_86a90
        function.argtypes = [ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86a90:.*st.*0x503a60",
                        r"86a98:.*stos.*0x504b94",
                        r"86aa0:.*call.*0xde630",
                        r"86aa8:.*mov.*0,g0",
                        r"86aac:.*call.*0x6fec0",
                        r"86ab4:.*mov.*0,g0",
                        r"86ab8:.*call.*0x6fec0",
                        r"86abc:.*call.*0xc8f60"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(0x12345678)
        assert result.marker_503a60 == 0x12345678
        assert result.halfword_504b94 == 0x5678
        assert list(result.call_targets) == [0xDE630, 0xC8F10, 0x6FEC0,
                                             0x9B308, 0x6FEC0, 0xC8F60]
        assert list(result.zero_argument_call_indices) == [2, 4]
        assert result.falls_through_to_86ac0 == 1
    print("recovered 0x86a90 service-prologue vectors: ok")


if __name__ == "__main__":
    main()
