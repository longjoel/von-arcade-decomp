#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_recovery_search_entry_84b7c.c"


class Entry(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "exits_to_84d60", "writes_509a6c", "value_509a6c",
        "search_index", "enters_search_84bb4")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "recovery-entry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_recovery_search_entry_84b7c
    build.argtypes = [ctypes.c_uint32]
    build.restype = Entry

    result = build(0)
    assert (result.exits_to_84d60, result.writes_509a6c,
            result.value_509a6c, result.search_index,
            result.enters_search_84bb4) == (1, 0, 0, 0, 0)
    result = build(1)
    assert (result.exits_to_84d60, result.writes_509a6c,
            result.value_509a6c, result.search_index,
            result.enters_search_84bb4) == (0, 1, 1, 0, 1)

print("recovered 0x84b7c recovery-search-entry vectors: ok")
