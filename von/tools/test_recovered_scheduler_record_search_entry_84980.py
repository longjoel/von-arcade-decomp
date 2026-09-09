#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_record_search_entry_84980.c"


class Entry(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "zero_product_exit_84b08", "writes_509a6c", "value_509a6c",
        "search_index", "enters_search_84994")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "search-entry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_record_search_entry_84980
    build.argtypes = [ctypes.c_int32]
    build.restype = Entry

    result = build(0)
    assert (result.zero_product_exit_84b08, result.writes_509a6c,
            result.value_509a6c, result.search_index,
            result.enters_search_84994) == (1, 0, 0, 0, 0)
    result = build(-100)
    assert (result.zero_product_exit_84b08, result.writes_509a6c,
            result.value_509a6c, result.search_index,
            result.enters_search_84994) == (0, 1, 1, 0, 1)

print("recovered 0x84980 record-search-entry vectors: ok")
