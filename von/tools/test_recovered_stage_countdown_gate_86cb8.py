"""Vectors for the 0x86cb8 countdown/call gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_countdown_gate_86cb8.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


@contextmanager
def build():
    wrapper = '#include "recovered_stage_countdown_gate_86cb8.c"\n'
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
                        ("counter_before", ctypes.c_uint32),
                        ("counter_after", ctypes.c_uint32),
                        ("flag_word_5024a4", ctypes.c_uint32),
                        ("exception_word_5024f4", ctypes.c_uint32),
                        ("decremented_address", ctypes.c_uint32),
                        ("calls_clear_service", ctypes.c_uint32),
                        ("clear_service_target", ctypes.c_uint32),
                        ("clear_service_argument", ctypes.c_uint32),
                        ("continuation", ctypes.c_uint32)]

        function = loaded.recovered_stage_countdown_gate_86cb8
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    listing = LISTING.read_text()
    for instruction in (r"86cb8:.*ld.*0x503a7c",
                        r"86cf4:.*subo.*1,g4,g4",
                        r"86cf8:.*st.*\(g5\)",
                        r"86d38:.*call.*0x1fe90",
                        r"86d3c:.*mov.*0,g0",
                        r"86db4:.*ret"):
        assert re.search(instruction, listing)

    with build() as function:
        result = function(1, 1, 0, 0, 0xCAFEBABE)
        assert (result.counter_after, result.calls_clear_service,
                result.continuation) == (0, 1, 0x86D38)

        result = function(1, 10, 1 << 4, 0, 0x12345678)
        assert result.counter_after == 9 and result.calls_clear_service == 1

        result = function(0, 97, 0, 0, 0x89ABCDEF)
        assert (result.counter_after, result.calls_clear_service,
                result.continuation) == (96, 0, 0x86DB4)
        result = function(1, 97, 0, 0x60, 0x11111111)
        assert result.calls_clear_service == 1
        result = function(1, 97, 0, 0x1234, 0x22222222)
        assert result.calls_clear_service == 0
        result = function(1, 100, 0, 0, 0x33333333)
        assert result.calls_clear_service == 0
        assert (result.decremented_address, result.clear_service_target,
                result.clear_service_argument) == (0x503A04, 0x1FE90,
                                                   0x33333333)
    print("recovered 0x86cb8 countdown-gate vectors: ok")


if __name__ == "__main__":
    main()
