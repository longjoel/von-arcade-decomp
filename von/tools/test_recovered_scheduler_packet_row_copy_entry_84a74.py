#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_packet_row_copy_entry_84a74.c"


class Entry(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "next_index", "wrapped", "source_byte_offset",
        "enters_copy_84a80")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "copy-entry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_packet_row_copy_entry_84a74
    build.argtypes = [ctypes.c_uint32]
    build.restype = Entry

    result = build(4)
    assert (result.next_index, result.wrapped,
            result.source_byte_offset, result.enters_copy_84a80) == (5, 0, 80, 1)
    result = build(59)
    assert (result.next_index, result.wrapped,
            result.source_byte_offset, result.enters_copy_84a80) == (0, 1, 0, 1)

print("recovered 0x84a74 packet-row-copy-entry vectors: ok")
