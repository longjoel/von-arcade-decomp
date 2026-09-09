"""Vectors for the 0x86d38 post-clear publication sequence."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_clear_publication_86d38.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_clear_publication_86d38.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))

        class Result(ctypes.Structure):
            _fields_ = [("service_targets", ctypes.c_uint32 * 3),
                        ("service_count", ctypes.c_uint32),
                        ("clear_service_g0", ctypes.c_uint32),
                        ("state_service_g0", ctypes.c_uint32),
                        ("publication_51c9a4", ctypes.c_uint32),
                        ("publication_51c9ac", ctypes.c_uint32),
                        ("value_503a70", ctypes.c_uint32),
                        ("value_503a78", ctypes.c_uint32),
                        ("command_value", ctypes.c_uint32),
                        ("state_marker", ctypes.c_uint32),
                        ("state_marker_halfword_address", ctypes.c_uint32),
                        ("state_marker_address_1", ctypes.c_uint32),
                        ("state_marker_address_2", ctypes.c_uint32),
                        ("state_address", ctypes.c_uint32),
                        ("phase_address", ctypes.c_uint32),
                        ("progress_address", ctypes.c_uint32),
                        ("command_address", ctypes.c_uint32),
                        ("continuation", ctypes.c_uint32)]

        function = loaded.recovered_stage_clear_publication_86d38
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86d38:.*call.*0x1fe90",
                        r"86d3c:.*mov.*0,g0",
                        r"86d40:.*call.*0x1f080",
                        r"86d48:.*st.*0x503a60",
                        r"86d78:.*0x423a8",
                        r"86d9c:.*stos.*0x5032f4",
                        r"86dac:.*st.*0x51c9c0"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(12, 0xB4, 7, 7, 0x12345678, 0xCAFEBABE)
        assert list(result.service_targets) == [0x1FE90, 0x1F080, 0x423A8]
        assert result.service_count == 3 and result.clear_service_g0 == 0xCAFEBABE
        assert result.state_service_g0 == 0
        assert result.command_value == 0x60
        assert result.publication_51c9a4 == 12
        assert result.publication_51c9ac == 0xB4
        result = function(19, 1, 8, 7, 0x89ABCDEF, 0xFFFFFFFF)
        assert result.command_value == 0x62
        assert (result.state_marker_halfword_address,
                result.state_marker_address_1, result.state_marker_address_2,
                result.state_address, result.phase_address,
                result.progress_address, result.command_address,
                result.continuation) == (0x51C942, 0x51D5E0, 0x51C9C0,
                                          0x503A60, 0x503A00, 0x503A04,
                                          0x5032F4, 0x86DB4)
    print("recovered 0x86d38 clear-publication vectors: ok")


if __name__ == "__main__":
    main()
