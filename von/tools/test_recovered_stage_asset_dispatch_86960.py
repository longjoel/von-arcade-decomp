"""Vectors for the 0x86960 stage asset dispatch plan."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_asset_dispatch_86960.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_asset_dispatch_86960.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("helper_arg0", ctypes.c_uint32),
                        ("helper_arg1", ctypes.c_uint32),
                        ("descriptor", ctypes.c_uint32),
                        ("target", ctypes.c_uint32),
                        ("target_arg1", ctypes.c_uint32),
                        ("target_arg2", ctypes.c_uint32)]

        function = loaded.recovered_stage_asset_dispatch_86960
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86960:.*addo.*31,20,g0",
                        r"86964:.*addo.*31,13,g1",
                        r"86974:.*bbc.*8",
                        r"86984:.*bbc.*9",
                        r"86994:.*bbc.*10",
                        r"869a8:.*call.*0x1dc90",
                        r"869c0:.*call.*0x1dc10"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(100, 200, 1 << 8)
        assert (result.helper_arg0, result.helper_arg1) == (131, 231)
        assert (result.descriptor, result.target) == (0x02FD8872, 0x1DC10)
        assert (result.target_arg1, result.target_arg2) == (1, 2)
        result = function(0xFFFFFFFF, 0, 0)
        assert result.helper_arg0 == 30
        assert (result.descriptor, result.target) == (0x02FD8876, 0x1DC10)
        result = function(0, 0, 1 << 9)
        assert result.descriptor == 0x02FD8872
        assert result.target == 0x1D7D0
        result = function(0, 0, 1 << 10)
        assert result.descriptor == 0x02FD8876
    print("recovered 0x86960 stage-asset dispatch vectors: ok")


if __name__ == "__main__":
    main()
