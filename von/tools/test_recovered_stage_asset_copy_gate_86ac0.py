"""Vectors for the 0x86ac0 conditional stage asset-copy gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_asset_copy_gate_86ac0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_asset_copy_gate_86ac0.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("initial_service", ctypes.c_uint32),
                        ("initial_service_argument", ctypes.c_uint32),
                        ("control_value", ctypes.c_uint32),
                        ("copies_enabled", ctypes.c_uint32),
                        ("copy_count", ctypes.c_uint32),
                        ("source", ctypes.c_uint32 * 2),
                        ("destination", ctypes.c_uint32 * 2),
                        ("length", ctypes.c_uint32 * 2),
                        ("continuation", ctypes.c_uint32)]

        function = loaded.recovered_stage_asset_copy_gate_86ac0
        function.argtypes = [ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86ac0:.*lda.*0x503ad0",
                        r"86ac8:.*call.*0x9baa0",
                        r"86ad8:.*cmpibne.*0x86b0c",
                        r"86aec:.*shlo.*9,3,g2",
                        r"86af0:.*call.*0xf5d40",
                        r"86b08:.*call.*0xf5d40"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(0x5A)
        assert result.initial_service == 0x9BAA0
        assert result.initial_service_argument == 0x503AD0
        assert result.copies_enabled == 1
        assert result.copy_count == 2
        assert list(result.source) == [0x51C9E0, 0x51CFE0]
        assert list(result.destination) == [0x503AD0, 0x5040D0]
        assert list(result.length) == [0x600, 0x600]
        assert result.continuation == 0x86B0C
        result = function(0x59)
        assert result.copies_enabled == 0
        assert result.copy_count == 0
    print("recovered 0x86ac0 asset-copy-gate vectors: ok")


if __name__ == "__main__":
    main()
