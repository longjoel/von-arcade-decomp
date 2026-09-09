#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("packed_byte_count", ctypes.c_uint32), ("first_target", ctypes.c_uint32),
        ("caller_target", ctypes.c_uint32), ("scan_call_count", ctypes.c_uint32),
        ("scan_target", ctypes.c_uint32 * 18), ("scanner_entry", ctypes.c_uint32),
        ("scanner_resume_entry", ctypes.c_uint32), ("selected_source", ctypes.c_uint32),
        ("copy_destination", ctypes.c_uint32), ("copy_halfword_count", ctypes.c_uint32),
        ("copy_byte_count", ctypes.c_uint32), ("source_publication_address", ctypes.c_uint32),
        ("destination_publication_address", ctypes.c_uint32), ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-record-reset-copy-") as d:
        so = Path(d) / "record-reset-copy.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_record_table_reset_copy_eb510.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_record_table_reset_copy_eb510
        fn.argtypes = [ctypes.c_uint32] * 2
        fn.restype = Result
        out = fn(0x1234, 0x1080000)
        assert (out.packed_byte_count, out.first_target, out.caller_target,
                out.scan_call_count, out.scanner_entry, out.scanner_resume_entry,
                out.selected_source, out.copy_destination, out.copy_halfword_count,
                out.copy_byte_count, out.source_publication_address,
                out.destination_publication_address, out.return_target) == (
                0x20000, 0xffff, 0x1234, 18, 0xeb450, 0xeb458, 0x1080000,
            0x501cc0, 0x10000, 0x20000, 0x501cc4, 0x501cc0, 0xeb5a8)
        assert list(out.scan_target) == [0xffff] + [1 << i for i in range(16)] + [0x1234]
        print("PASS: 0xeb510 runtime record reset/copy")


if __name__ == "__main__":
    main()
