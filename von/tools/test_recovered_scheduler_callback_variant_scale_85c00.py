"""Vectors for the stable 0x85c00 callback setup prefix."""

import ctypes
import pathlib
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_variant_scale_85c00.c"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_variant_scale_85c00.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))
        class Result(ctypes.Structure):
            _fields_ = [("object_4a", ctypes.c_int16),
                        ("object_190", ctypes.c_int32),
                        ("related_state", ctypes.c_int32),
                        ("related_source", ctypes.c_int32),
                        ("quotient", ctypes.c_int32),
                        ("working_value", ctypes.c_int32),
                        ("uses_related_source", ctypes.c_uint32)]
        function = loaded.recovered_scheduler_callback_variant_scale_85c00
        function.argtypes = [ctypes.c_int16, ctypes.c_int32, ctypes.c_int32,
                             ctypes.c_int32, ctypes.c_int32]
        function.restype = Result
        yield function


def main():
    with build() as function:
        result = function(-12, 1, 11, 350, 900)
        assert result.working_value == 0
        assert result.uses_related_source == 0

        result = function(-12, 0, 11, 350, 900)
        assert result.related_source == 350
        assert result.quotient == 3
        assert result.working_value == -36
        assert result.uses_related_source == 1

        result = function(20, 0, 14, 999, 250)
        assert result.related_source == 250
        assert result.quotient == 2
        assert result.working_value == 40

        result = function(20, 0, 7, 999, 250)
        assert result.working_value == 20
        assert result.uses_related_source == 0
    print("recovered 0x85c00 variant-scale vectors: ok")


if __name__ == "__main__":
    main()
