#!/usr/bin/env python3
"""Validate the primary/secondary slot-20 selector graph distinction."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "von/i960/recovered_startup_mode4_arm_86eec_response_selector.c"
SECONDARY = ROOT / "von/i960/recovered_startup_mode4_arm_873dc_secondary_selector.c"


class PrimaryResult(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "response_value", "response_source_address",
        "special_response", "special_store_address", "special_store_value",
        "special_path", "response_mask", "response_byte", "normalized_response",
        "normalization_remainder", "threshold", "threshold_exceeded", "dispatch_table_address",
        "dispatch_index", "dispatch_slot_address", "dispatch_target", "continuation_target")]


class SecondaryResult(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "status_value", "response_value", "response_mask", "normalized_response",
        "status_source_address", "response_source_address",
        "special_response", "special_mode", "special_store_address", "special_store_value",
        "special_path", "special_target", "response_byte", "normalization_remainder",
        "threshold", "failure_target", "table_address", "dispatch_index",
        "dispatch_slot_address", "dispatch_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        primary_so = pathlib.Path(directory) / "primary.so"
        secondary_so = pathlib.Path(directory) / "secondary.so"
        for source, output in ((PRIMARY, primary_so), (SECONDARY, secondary_so)):
            subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                            str(source), "-o", str(output)], check=True)
        primary = ctypes.CDLL(str(primary_so)).recovered_startup_mode4_arm_86eec_response_selector
        primary.argtypes = [ctypes.c_uint32, ctypes.POINTER(PrimaryResult)]
        primary.restype = ctypes.c_int
        secondary = ctypes.CDLL(str(secondary_so)).recovered_startup_mode4_arm_873dc_secondary_selector
        secondary.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(SecondaryResult)]
        secondary.restype = ctypes.c_int

        primary_targets = {1: 0x871f4, 0x1f: 0x87210, 0x49: 0x8729c, 0xa9: 0x8737c}
        secondary_targets = {1: 0x876e8, 0x1f: 0x87704, 0x49: 0x8779c, 0xa9: 0x87888}
        for response in primary_targets:
            p, s = PrimaryResult(), SecondaryResult()
            assert primary(response, ctypes.byref(p)) == 1
            assert secondary(0, response, ctypes.byref(s)) == 1
            assert p.normalized_response == s.normalized_response == response
            assert p.normalization_remainder == s.normalization_remainder == 0
            assert p.dispatch_target == primary_targets[response]
            assert s.dispatch_target == secondary_targets[response]
            assert p.dispatch_target != s.dispatch_target
            assert p.dispatch_slot_address == 0x86f34 + response * 4
            assert s.dispatch_slot_address == 0x87428 + response * 4

        p, s = PrimaryResult(), SecondaryResult()
        assert primary(10, ctypes.byref(p)) == 1
        assert secondary(0, 10, ctypes.byref(s)) == 1
        assert p.special_path == 1 and p.special_store_value == 8
        assert s.special_path == 1 and s.special_store_value == 9
        assert p.continuation_target == 0x873cc and s.special_target == 0x878d8
    print("PASS: primary/secondary slot-20 selector graph")


if __name__ == "__main__":
    main()
