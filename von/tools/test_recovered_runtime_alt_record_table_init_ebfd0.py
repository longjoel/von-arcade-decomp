#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "workspace_base", "packed_byte_count", "first_target", "shifted_target_first",
        "shifted_target_last", "caller_target", "scan_call_count")] + [
        ("scan_target", ctypes.c_uint32 * 18), ("scanner_address", ctypes.c_uint32),
        ("match_slot_address", ctypes.c_uint32 * 2), ("normalized_match_value", ctypes.c_uint32),
        ("status_counter_before", ctypes.c_uint32), ("status_counter_after", ctypes.c_uint32),
        ("status_counter_address", ctypes.c_uint32), ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-record-init-ebfd0-") as d:
        so = Path(d) / "init.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I",
                        str(ROOT / "von/i960"), "-o", str(so), str(ROOT /
                        "von/i960/recovered_runtime_alt_record_table_init_ebfd0.c")], check=True)
        fn = ctypes.CDLL(str(so)).recovered_runtime_alt_record_table_init_ebfd0
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]; fn.restype = Result
        out = fn(0x89abcdef, 20)
        assert (out.workspace_base, out.packed_byte_count, out.scan_call_count,
                out.scanner_address, out.status_counter_after, out.return_target) == (
            0x1800000, 0x4000, 18, 0xebf10, 21, 0xec084)
        assert list(out.scan_target) == [0xffff] + [1 << i for i in range(16)] + [0x89abcdef]
        assert list(out.match_slot_address) == [0x578588, 0x57858c]
        print("PASS: 0xebfd0 alternate record initializer")


if __name__ == "__main__":
    main()
