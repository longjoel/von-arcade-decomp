#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def assert_listing_dataflow():
    listing = LISTING.read_text(encoding="utf-8")
    required = (
        ("eac98:", "ld\t0x884000,g4"),
        ("eacc0:", "subrl\tfp0,g6,g6"),
        ("ead08:", "st\tg6,0x5783f8"),
        ("ead10:", "notbit\t31,g6,g6"),
    )
    for address, text in required:
        assert any(address in line and text in line for line in listing.splitlines()), \
            f"eac84 listing dataflow missing: {address} {text}"


class Result(ctypes.Structure):
    _fields_ = [
        ("workspace_word_10_sum", ctypes.c_uint32), ("fifo_response_opcode_30", ctypes.c_uint32),
        ("fifo_response_opcode_10", ctypes.c_uint32), ("division_result_g6", ctypes.c_uint32),
        ("state_word_g2", ctypes.c_uint32),
        ("first_packet_response_r4", ctypes.c_uint32), ("packet_20", ctypes.c_uint32 * 2),
        ("packet_21", ctypes.c_uint32 * 2), ("packet_18", ctypes.c_uint32 * 4),
        ("packet_20_count", ctypes.c_uint32), ("packet_21_count", ctypes.c_uint32),
        ("packet_18_count", ctypes.c_uint32), ("masked_fifo_word", ctypes.c_uint32),
        ("negative_state_address", ctypes.c_uint32), ("state_3f8", ctypes.c_uint32),
        ("state_3f8_address", ctypes.c_uint32), ("fifo_address", ctypes.c_uint32),
        ("opcode_20", ctypes.c_uint32), ("opcode_21", ctypes.c_uint32),
        ("opcode_18", ctypes.c_uint32), ("next_target", ctypes.c_uint32),
    ]


def main():
    assert_listing_dataflow()
    with tempfile.TemporaryDirectory(prefix="von-event-setup-finalize-") as d:
        so = Path(d) / "event-setup-finalize.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_event_setup_finalize_eac84.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_event_setup_finalize_eac84
        fn.argtypes = [ctypes.c_uint32] * 6
        fn.restype = Result
        out = fn(0x100, 0x200, 0x12345678, 0x300, 0x500, 0x600)
        assert (out.masked_fifo_word, out.negative_state_address,
                out.state_3f8) == (0x5678, 0xffa87c1c, 0x300)
        assert list(out.packet_20) == [20, 0x5678]
        assert list(out.packet_21) == [21, 0xffa87c1c]
        assert list(out.packet_18) == [18, 0x80000500, 0x80000600, 0x80000300]
        assert (out.packet_20_count, out.packet_21_count, out.packet_18_count,
                out.state_3f8_address, out.fifo_address, out.opcode_20,
                out.opcode_21, out.opcode_18, out.next_target) == (
            2, 2, 4, 0x5783f8, 0x884000, 20, 21, 18, 0xead1c)
        print("PASS: 0xeac84 event setup final packets")


if __name__ == "__main__":
    main()
