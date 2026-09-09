#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_recovery_row_seed_84bec.c"


class Seed(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_index", "wrapped", "source_byte_offset", "scan_limit",
        "mask", "loaded_low_nibble")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "recovery-seed.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_recovery_row_seed_84bec
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    build.restype = Seed

    result = build(8, 0xabcd)
    assert (result.source_index, result.wrapped, result.source_byte_offset,
            result.scan_limit, result.mask,
            result.loaded_low_nibble) == (7, 0, 112, 59, 0xffff, 13)
    result = build(0, 0x1234)
    assert (result.source_index, result.wrapped,
            result.source_byte_offset, result.loaded_low_nibble) == (59, 1, 944, 4)

print("recovered 0x84bec recovery-row-seed vectors: ok")
