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
    required = (("eabdc:", "stos\tg14,0x5783e6"),
                ("eabe4:", "stos\tg14,0x5783e8"),
                ("eabec:", "stos\tg1,0x5783e4"),
                ("eabfc:", "st\tg13,0x5783ec"))
    for address, text in required:
        assert any(address in line and text in line for line in listing.splitlines()), \
            f"eab48 listing dataflow missing: {address} {text}"


class Result(ctypes.Structure):
    _fields_ = [
        ("prior_fifo_word", ctypes.c_uint32), ("workspace_word_8_left", ctypes.c_uint32),
        ("workspace_word_8_right", ctypes.c_uint32), ("phase_word", ctypes.c_uint32),
        ("phase_word_plus_0x4000", ctypes.c_uint32), ("masked_phase_word", ctypes.c_uint32),
        ("extended_real_word", ctypes.c_uint32), ("converted_extended_real_word", ctypes.c_uint32),
        ("divided_extended_real_word", ctypes.c_uint32), ("preserved_g14_word", ctypes.c_uint32),
        ("workspace_word_8_sum", ctypes.c_uint32), ("packet_first", ctypes.c_uint32 * 3),
        ("packet_second", ctypes.c_uint32 * 3), ("state_3e4", ctypes.c_uint32),
        ("state_3e6", ctypes.c_uint32), ("state_3e8", ctypes.c_uint32),
        ("state_3ec", ctypes.c_uint32), ("state_3f0", ctypes.c_uint32),
        ("state_3f4", ctypes.c_uint32), ("state_address_base", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32), ("geometry_command", ctypes.c_uint32),
        ("completion_command", ctypes.c_uint32), ("next_target", ctypes.c_uint32),
    ]


def main():
    assert_listing_dataflow()
    with tempfile.TemporaryDirectory(prefix="von-event-setup-state-") as d:
        so = Path(d) / "event-setup-state.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_event_setup_state_prefix_eab48.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_event_setup_state_prefix_eab48
        fn.argtypes = [ctypes.c_uint32] * 8
        fn.restype = Result
        out = fn(0x1111, 0xdeadff00, 0x20, 0x30, 0x40618000,
                 0x12345678, 0x87654321, 0x55)
        assert (out.phase_word_plus_0x4000, out.masked_phase_word,
                out.workspace_word_8_sum) == (0xdeadff00 + 0x4000, 0x3f00, 0x50)
        assert list(out.packet_first) == [29, 0x3f00, 0x40618000]
        assert list(out.packet_second) == [30, 0x3f00, 0x40618000]
        assert (out.state_3e4, out.state_3e6, out.state_3e8, out.state_3ec,
                out.state_3f0, out.state_3f4, out.state_address_base,
                out.fifo_address, out.next_target) == (
            0xdeadff00 + 0x4000, 0x55, 0x55, 0x40618000, 0x12345678,
            0x87654321, 0x5783e4, 0x884000, 0xeac1c)
        print("PASS: 0xeab48 event setup state prefix")


if __name__ == "__main__":
    main()
