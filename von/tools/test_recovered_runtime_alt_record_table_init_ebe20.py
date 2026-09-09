#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "workspace_base", "packed_byte_count", "first_target", "shifted_target_first",
        "shifted_target_last", "caller_target", "scan_call_count")] + [
        ("scan_target", ctypes.c_uint32 * 18), ("scanner_address", ctypes.c_uint32),
        ("match_slot_address", ctypes.c_uint32 * 4), ("normalized_match_value", ctypes.c_uint32),
        ("status_counter_before", ctypes.c_uint32), ("status_counter_after", ctypes.c_uint32),
        ("status_counter_address", ctypes.c_uint32), ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-alt-record-init-ebe20-") as d:
        so = Path(d) / "init.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I",
                        str(ROOT / "von/i960"), "-o", str(so), str(ROOT /
                        "von/i960/recovered_runtime_alt_record_table_init_ebe20.c")], check=True)
        fn = ctypes.CDLL(str(so)).recovered_runtime_alt_record_table_init_ebe20
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]; fn.restype = Result
        out = fn(0x12345678, 11)
        assert (out.workspace_base, out.packed_byte_count, out.scan_call_count,
                out.scanner_address, out.status_counter_after, out.return_target) == (
            0x1080000, 0x80000, 18, 0xebd20, 12, 0xebf04)
        assert list(out.scan_target) == [0xffff] + [1 << i for i in range(16)] + [0x12345678]
        assert list(out.match_slot_address) == [0x578578, 0x57857c, 0x578580, 0x578584]
        print("PASS: 0xebe20 paired alternate record initializer")


if __name__ == "__main__":
    main()
