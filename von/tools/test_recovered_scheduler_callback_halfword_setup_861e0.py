"""Vectors for the 0x861e0 callback halfword setup."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_halfword_setup_861e0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_halfword_setup_861e0.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))
        class Result(ctypes.Structure):
            _fields_ = [("input_g0", ctypes.c_int16),
                        ("input_g1", ctypes.c_int16),
                        ("value_503b18", ctypes.c_int16),
                        ("value_503b1a", ctypes.c_int16),
                        ("stored_509b94", ctypes.c_int32),
                        ("stored_509b98", ctypes.c_int32),
                        ("zeroed_by_503b18", ctypes.c_uint32),
                        ("overridden_by_503b1a", ctypes.c_uint32),
                        ("return_stub", ctypes.c_uint32)]
        function = loaded.recovered_scheduler_callback_halfword_setup_861e0
        function.argtypes = [ctypes.c_int16, ctypes.c_int16,
                             ctypes.c_int16, ctypes.c_int16]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"861f8:.*shlo.*16,g0,g0",
                        r"8620c:.*cmpi.*g4,0",
                        r"86224:.*cmpibe.*0,g4,0x8622c",
                        r"86234:.*bx.*\(g2\)"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(-7, 123, 4, 0)
        assert result.stored_509b94 == -7
        assert result.stored_509b98 == 123
        assert result.zeroed_by_503b18 == 0
        assert result.return_stub == 0x86238

        result = function(0x1234, -9, 0, 0)
        assert result.stored_509b94 == 0x1234
        assert result.stored_509b98 == 0
        assert result.zeroed_by_503b18 == 1

        result = function(2, 3, 0, -11)
        assert result.stored_509b98 == -11
        assert result.overridden_by_503b1a == 1
    print("recovered 0x861e0 halfword-setup vectors: ok")


if __name__ == "__main__":
    main()
