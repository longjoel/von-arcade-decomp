#!/usr/bin/env python3
"""Contract for the fork's debugger PC tracking and M2COMM diagnostics.

These used to live in the core MAME patch profile; they are now committed in
the `mame-von` fork (see `mame/`). The behavior they guard is what the
captures were taken with.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEBUG_H = ROOT / "mame/src/emu/debug/debugcpu.h"
DEBUG_CPP = ROOT / "mame/src/emu/debug/debugcpu.cpp"
M2COMM = ROOT / "mame/src/mame/sega/m2comm.cpp"


def main() -> int:
    debugger = DEBUG_H.read_text(encoding="utf-8") + DEBUG_CPP.read_text(encoding="utf-8")
    for fragment in ("m_track_pc_addresses", "track_pc_data_clear", "unordered_set"):
        if fragment not in debugger:
            raise SystemExit(f"debugger PC-address tracking missing {fragment}")
    m2comm = M2COMM.read_text(encoding="utf-8")
    for fragment in (
        "diag listen failure",
        "diag connect failure",
        "diag sockets ready",
        "diag handshake timer",
        "m_diagnostics",
    ):
        if fragment not in m2comm:
            raise SystemExit(f"M2COMM diagnostics missing {fragment}")
    print("PASS: fork debugger PC-tracking and M2COMM diagnostics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
