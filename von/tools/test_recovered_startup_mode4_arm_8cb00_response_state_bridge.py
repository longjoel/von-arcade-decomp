#!/usr/bin/env python3
"""Vectors for the 0x8cb00 response/state bridge."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8cb00_response_state_bridge.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "first_fifo_response", "second_fifo_response", "current_record_8",
        "current_record_10", "state_51c940", "state_51c948", "state_51c950",
        "state_51c954", "timing_5770f0", "adjusted_timing", "helper_result",
        "selected_float", "timing_zero_path")]
    _fields_ += [(name, ctypes.c_uint32 * 3) for name in ("command_29_packet", "command_30_packet")]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "helper_input_x", "helper_input_y", "helper_call", "positive_fallback",
        "fifo_address", "command_29", "command_30", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8cafc:.*ld.*0x884000,g2", r"8cb04:.*mov.*29,r12",
        r"8cb18:.*lda.*0x3000\(g2\),g4", r"8cb20:.*and.*g5,g4,g4",
        r"8cb2c:.*lda.*0x42200000,g5", r"8cb3c:.*ld.*0x884000,g1",
        r"8cb44:.*ld.*0x8\(g0\),g7", r"8cb48:.*mov.*30,r13",
        r"8cb64:.*ld.*0x884000,g6", r"8cb6c:.*ld.*0x10\(g0\),g4",
        r"8cb70:.*subr.*g1,g7,g0", r"8cb74:.*addr.*g6,g4,g1",
        r"8cb80:.*stos.*g2,0x51c940", r"8cb88:.*st.*g5,0x51c948",
        r"8cb90:.*subo.*3,g4,g4", r"8cb94:.*cmpo.*1,g4",
        r"8cba8:.*bl.*0x8cbe0", r"8cbb4:.*call.*0x6ece0",
        r"8cbec:.*cmpibne.*0,g4,0x8cc0c"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "bridge.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8cb00_response_state_bridge
        function.argtypes = [ctypes.c_uint32] * 6
        function.restype = Result
        result = function(0x12345678, 0x1000, 0x30, 0x220, 5, 0xbf800000)
        assert (result.state_51c940, result.state_51c948, result.state_51c950,
                result.state_51c954) == (0x12345678, 0x42200000, 0x12345648, 0x1220)
        assert list(result.command_29_packet) == [29, 0x8678, 0x42200000]
        assert list(result.command_30_packet) == [30, 0x8678, 0x42200000]
        assert (result.selected_float, result.adjusted_timing,
                result.timing_zero_path, result.continuation) == (0xbf800000, 2, 0, 0x8cc0c)
    print("recovered 0x8cb00 response/state-bridge vectors: ok")


if __name__ == "__main__":
    main()
