#!/usr/bin/env python3
"""Trace-validate the tile-control bus write on live MMIO traffic.

The 45-second no-input boot capture shows 102 writes to the tile-control
register at 0x01800000. Five come from pc=0x1cd00, the store inside the
0x1ccf8 tile/control bus wrapper, with data 0000, 8000, 7fff, 0000, 5940
in that order. The remaining 97 (96 from 0x2b8bc, one from 0x0f5e04) are
recorded here as unattributed context: they prove the register is shared,
but only the wrapper path pins the recovered unit.

This test replays the five wrapper-path writes through the compiled bus
plan (recovered_text_tile_control_bus): each observed value must come back
unchanged with the bus address 0x01800000.
"""
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text.c"
MEMORY_SOURCE = ROOT / "von/i960/recovered_memory.c"
HOST_CONTROL_SOURCE = ROOT / "von/i960/recovered_host_control.c"

# (pc, address, data) in trace order for the 0x1ccf8 wrapper path.
WRAPPER_WRITES = [
    (0x1CD00, 0x01800000, 0x0000),
    (0x1CD00, 0x01800000, 0x8000),
    (0x1CD00, 0x01800000, 0x7FFF),
    (0x1CD00, 0x01800000, 0x0000),
    (0x1CD00, 0x01800000, 0x5940),
]


def main() -> int:
    assert len(WRAPPER_WRITES) == 5, "fixture covers the 5 wrapper-path writes"
    with tempfile.TemporaryDirectory(prefix="von-text-control-trace-") as directory:
        library = Path(directory) / "text-control-trace.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                "-shared",
                "-fPIC",
                "-O2",
                SOURCE,
                MEMORY_SOURCE,
                HOST_CONTROL_SOURCE,
                "-o",
                library,
            ],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_text_tile_control_bus.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_tile_control_bus.restype = ctypes.c_uint32
        for pc, address, data in WRAPPER_WRITES:
            if pc != 0x1CD00 or address != 0x01800000:
                raise SystemExit(
                    f"fixture attribution drift: pc=0x{pc:05x} address=0x{address:08x}"
                )
            actual_address = ctypes.c_uint32()
            actual = recovered.recovered_text_tile_control_bus(
                data, ctypes.byref(actual_address)
            )
            if actual != data or actual_address.value != 0x01800000:
                raise SystemExit(
                    f"tile-control oracle mismatch data=0x{data:04x}: "
                    f"address=0x{actual_address.value:08x}, value=0x{actual:08x}"
                )
    print("PASS: 5 wrapper-path tile-control writes match the live oracle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
