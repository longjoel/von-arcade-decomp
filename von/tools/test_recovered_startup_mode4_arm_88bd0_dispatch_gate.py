#!/usr/bin/env python3
"""Vectors for the 0x88bd0 shared dispatch gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_88bd0_dispatch_gate.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51d5e0_before", "state_51d5e0_after", "timing_51d5e4",
        "marker_51c9b8", "flag_51c99c_before", "flag_51c99c_after",
        "response_51c998", "response_51c9a0_before", "response_51c9a0_after",
        "status_byte", "counter_51c984", "g14_value", "initial_gate_passed",
        "status_gate_passed", "dispatch_selector", "dispatch_table_address",
        "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88bd0:.*addo.*16,sp,sp", r"88bd4:.*ld.*0x51d5e0",
                        r"88be4:.*cmpi.*g4,0", r"88bf8:.*ld.*0x51c9b8",
                        r"88c00:.*cmpibne.*g5,g4,0x88c10",
                        r"88c08:.*st.*0x51d5e0", r"88c18:.*cmpibl.*1,g4,0x88c54",
                        r"88c68:.*ld.*0x51c998", r"88c70:.*cmpibne.*g5,g4,0x88c7c",
                        r"88c74:.*st.*g14,0x51c9a0", r"88c88:.*ldob.*\(g4\)\[r7\]",
                        r"88c98:.*cmpibne.*1,g4,0x88cc8", r"88cc8:.*mov.*2,r12",
                        r"88cd4:.*ld.*0x51c99c", r"88ce8:.*bx.*\(g4\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_88bd0_dispatch_gate
        function.argtypes = [ctypes.c_uint32] * 9
        function.restype = Result
        result = function(0, 5, 5, 1, 5, 1, 7, 10, 1)
        assert (result.state_51d5e0_after, result.response_51c9a0_after,
                result.flag_51c99c_after, result.dispatch_selector,
                result.status_gate_passed) == (1, 1, 1, 1, 1)
        result = function(0, 5, 4, 1, 6, 0, 7, 10, 1)
        assert (result.response_51c9a0_after, result.flag_51c99c_after,
                result.dispatch_selector) == (0, 2, 2)
        result = function(1, 5, 4, 0, 5, 0, 7, 10, 1)
        assert result.initial_gate_passed == 0 and result.flag_51c99c_after == 0
        result = function(0, 5, 4, 1, 5, 0, 0, 10, 1)
        assert result.status_gate_passed == 0 and result.flag_51c99c_after == 1
        result = function(0, 5, 4, 1, 5, 0, 0, 0x96, 7)
        assert result.flag_51c99c_after == 7 and result.dispatch_selector == 7
        assert (result.dispatch_table_address, result.continuation) == (0x88cec, 0x88cd4)
    print("recovered 0x88bd0 dispatch-gate vectors: ok")


if __name__ == "__main__":
    main()
