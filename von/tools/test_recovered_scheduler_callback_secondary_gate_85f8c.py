"""Vectors for the 0x85f8c secondary callback-map routing gate."""

import ctypes
import pathlib
import subprocess
import tempfile
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_scheduler_callback_secondary_gate_85f8c.c"


@contextmanager
def build():
    wrapper = '#include "recovered_scheduler_callback_secondary_gate_85f8c.c"\n'
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "wrapper.c"
        path.write_text(wrapper)
        library = pathlib.Path(directory) / "lib.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O0",
                        "-I", str(SOURCE.parent), str(path), "-o", str(library)],
                       check=True)
        loaded = ctypes.CDLL(str(library))
        class Result(ctypes.Structure):
            _fields_ = [("candidate_index", ctypes.c_uint32),
                        ("route", ctypes.c_uint32),
                        ("map_bit6", ctypes.c_uint32),
                        ("previous_special_bits", ctypes.c_uint32),
                        ("current_is_zero", ctypes.c_uint32),
                        ("object_byte_is_zero", ctypes.c_uint32)]
        function = loaded.recovered_scheduler_callback_secondary_gate_85f8c
        array_u8 = ctypes.POINTER(ctypes.c_uint8)
        array_u16 = ctypes.POINTER(ctypes.c_uint16)
        function.argtypes = [array_u8, array_u16, array_u16, array_u8]
        function.restype = Result
        yield function


def main():
    with build() as function:
        maps = (ctypes.c_uint8 * 32)(*[0] * 32)
        previous = (ctypes.c_uint16 * 32)(*[0] * 32)
        current = (ctypes.c_uint16 * 32)(*[1] * 32)
        objects = (ctypes.c_uint8 * 32)(*[1] * 32)
        result = function(maps, previous, current, objects)
        assert result.route == 0
        maps[7] = 0x40
        result = function(maps, previous, current, objects)
        assert result.candidate_index == 7
        assert result.route == 2

        previous[7] = 1 << 9
        result = function(maps, previous, current, objects)
        assert result.route == 1
        previous[7] = 0
        current[7] = 0
        result = function(maps, previous, current, objects)
        assert result.route == 1
        current[7] = 1
        objects[7] = 0
        result = function(maps, previous, current, objects)
        assert result.route == 1
    print("recovered 0x85f8c secondary-gate vectors: ok")


if __name__ == "__main__":
    main()
