#!/usr/bin/env python3
"""Test deterministic parts of the recovered host interrupt helper."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_host_control.c"


def expected_timer(mask: int) -> tuple[int, int]:
    return {
        4: (0x00F00000, 0x000186A0),
        8: (0x00F00004, 0x000FFFFF),
        16: (0x00F00008, 0x000FFFFF),
        32: (0x00F0000C, 0x000FFFFF),
    }.get(mask, (0, 0))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-host-control-") as directory:
        library = Path(directory) / "host-control.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_host_interrupt_route.argtypes = [ctypes.c_uint32]
        recovered.recovered_host_interrupt_route.restype = ctypes.c_uint32
        recovered.recovered_host_timer_initial_value.restype = ctypes.c_uint32
        recovered.recovered_host_initial_interrupt_control.restype = ctypes.c_uint32
        for name in ("recovered_host_timer_address", "recovered_host_timer_reload"):
            function = getattr(recovered, name)
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32

        vectors = 0
        for mask in range(0x10000):
            address, reload_value = expected_timer(mask)
            actual_address = recovered.recovered_host_timer_address(mask)
            actual_reload = recovered.recovered_host_timer_reload(mask)
            if (actual_address, actual_reload) != (address, reload_value):
                raise SystemExit(
                    f"timer mapping mismatch mask=0x{mask:04x}: "
                    f"0x{actual_address:08x}/0x{actual_reload:08x} != "
                    f"0x{address:08x}/0x{reload_value:08x}"
                )
            vectors += 1

        if recovered.recovered_host_timer_initial_value() != 0x00061A80:
            raise SystemExit("initial timer value mismatch")
        if recovered.recovered_host_initial_interrupt_control() != 0x0000023D:
            raise SystemExit("initial interrupt control mismatch")

        expected_routes = {
            0x00000001: 1,
            0x00000002: 2,
            0x00000080: 0,
            0x00000200: 3,
            0x00000400: 4,
            0x00000800: 2,
        }
        for mask in range(0x10000):
            expected = expected_routes.get(
                mask, 5 if mask > 0x80 else 0
            )
            actual = recovered.recovered_host_interrupt_route(mask)
            if actual != expected:
                raise SystemExit(
                    f"interrupt route mismatch mask=0x{mask:04x}: "
                    f"{actual} != {expected}"
                )

    print(
        f"PASS: {vectors:,} host interrupt-mask vectors, "
        "65,536 dispatcher routes, and timer bootstrap constants"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
