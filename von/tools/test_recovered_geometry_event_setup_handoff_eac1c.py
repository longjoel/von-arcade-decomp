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
    required = (("eac38:", "st\tg14,0x578400"),
                ("eac40:", "st\tg14,0x5783fc"),
                ("eac48:", "ld\t0x884000,g0"),
                ("eac84:", "mov\t20,r6"))
    for address, text in required:
        assert any(address in line and text in line for line in listing.splitlines()), \
            f"eac1c listing dataflow missing: {address} {text}"


class Result(ctypes.Structure):
    _fields_ = [
        ("masked_phase_word", ctypes.c_uint32), ("extended_real_word", ctypes.c_uint32),
        ("preserved_g14_word", ctypes.c_uint32), ("fifo_response_after_packet", ctypes.c_uint32),
        ("packet_replay", ctypes.c_uint32 * 3), ("packet_delta", ctypes.c_uint32 * 3),
        ("event_counter", ctypes.c_uint32), ("event_counter_address", ctypes.c_uint32),
        ("rolling_counter", ctypes.c_uint32), ("rolling_counter_address", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32), ("replay_command", ctypes.c_uint32),
        ("delta_command", ctypes.c_uint32), ("geometry_constant", ctypes.c_uint32),
        ("next_target", ctypes.c_uint32),
    ]


def main():
    assert_listing_dataflow()
    with tempfile.TemporaryDirectory(prefix="von-event-setup-handoff-") as d:
        so = Path(d) / "event-setup-handoff.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_event_setup_handoff_eac1c.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_event_setup_handoff_eac1c
        fn.argtypes = [ctypes.c_uint32] * 4
        fn.restype = Result
        out = fn(0x1234, 0x40618000, 0x77, 0x89ab)
        assert list(out.packet_replay) == [30, 0x1234, 0x40618000]
        assert list(out.packet_delta) == [10, 0x40618000, 0x430c0000]
        assert (out.event_counter, out.event_counter_address, out.rolling_counter,
                out.rolling_counter_address, out.fifo_address, out.replay_command,
                out.delta_command, out.geometry_constant, out.next_target) == (
            0x77, 0x578400, 0x77, 0x5783fc, 0x884000, 30, 10,
            0x430c0000, 0xeac84)
        print("PASS: 0xeac1c event setup handoff")


if __name__ == "__main__":
    main()
