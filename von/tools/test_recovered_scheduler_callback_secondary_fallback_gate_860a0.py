"""Vectors for the 0x860a0 secondary-map fallback gate."""

import ctypes
import pathlib
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_secondary_fallback_gate_860a0.c"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_secondary_fallback_gate_860a0.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))
        class Result(ctypes.Structure):
            _fields_ = [("map_bit6", ctypes.c_uint32),
                        ("previous_bit10", ctypes.c_uint32),
                        ("working_value", ctypes.c_uint32),
                        ("continues_to_860d4", ctypes.c_uint32),
                        ("rejects_to_86174", ctypes.c_uint32)]
        function = loaded.recovered_scheduler_callback_secondary_fallback_gate_860a0
        function.argtypes = [ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        yield function


def main():
    with build() as function:
        result = function(0x40, 0, 0)
        assert result.continues_to_860d4 == 0
        assert result.rejects_to_86174 == 1

        result = function(0x40, 1 << 10, 0)
        assert result.previous_bit10 == 1
        assert result.continues_to_860d4 == 1

        result = function(0x40, 0, 7)
        assert result.continues_to_860d4 == 1

        result = function(0, 1 << 10, 7)
        assert result.rejects_to_86174 == 1
    print("recovered 0x860a0 fallback-gate vectors: ok")


if __name__ == "__main__":
    main()
