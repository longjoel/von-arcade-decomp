#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_flag_synthesis_84368.c"


class Flags(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "value_509a60", "set_bit0", "set_bit1", "set_bit2", "set_bit3",
        "set_bit4", "set_bit5", "set_bit2_or_3_final")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-flags.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_flag_synthesis_84368
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    build.restype = Flags

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Flags._fields_)

    assert values(0, 0, 0) == (0, 0, 0, 0, 0, 0, 0, 0)
    assert values(0, 0x100, 0x700) == (1 << 4 | 1 << 1 | 1 << 3,
                                       0, 1, 0, 1, 1, 0, 0)
    assert values(0, 0x700, 0x700) == (1 | 1 << 2 | 1 << 4,
                                       1, 0, 1, 0, 1, 0, 0)
    assert values(0x20, 0, 0x200) == (0x22, 0, 1, 0, 0, 0, 0, 0)
    assert values(0, 0x20000, 0) == (1 << 2, 0, 0, 0, 0, 0, 0, 1)
    assert values(0, 0, 0x20000) == (1 << 3, 0, 0, 0, 0, 0, 0, 1)
    assert values(1 << 3, 0x20000, 0x20000) == (1 << 3 | 1 << 2,
                                                 0, 0, 0, 0, 0, 0, 1)

print("recovered 0x84368 flag-synthesis vectors: ok")
