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
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


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
        class DispatchPlan(ctypes.Structure):
            _fields_ = [("mask", ctypes.c_uint32),
                        ("control_before", ctypes.c_uint32),
                        ("control_after", ctypes.c_uint32),
                        ("control_address", ctypes.c_uint32),
                        ("control_mmio_address", ctypes.c_uint32),
                        ("route", ctypes.c_uint32)]

        recovered.recovered_host_interrupt_dispatch_plan.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(DispatchPlan)]
        recovered.recovered_host_interrupt_dispatch_plan.restype = ctypes.c_uint32
        class MaskUpdatePlan(ctypes.Structure):
            _fields_ = [("mask", ctypes.c_uint32),
                        ("control_before", ctypes.c_uint32),
                        ("control_cleared", ctypes.c_uint32),
                        ("control_rearmed", ctypes.c_uint32),
                        ("control_address", ctypes.c_uint32),
                        ("control_mmio_address", ctypes.c_uint32),
                        ("timer_address", ctypes.c_uint32),
                        ("timer_reset_value", ctypes.c_uint32),
                        ("timer_reload_value", ctypes.c_uint32),
                        ("timer_write_count", ctypes.c_uint32),
                        ("acknowledge_address", ctypes.c_uint32),
                        ("acknowledge_value", ctypes.c_uint32)]

        recovered.recovered_host_interrupt_mask_update_plan.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(MaskUpdatePlan)]
        recovered.recovered_host_interrupt_mask_update_plan.restype = ctypes.c_uint32
        recovered.recovered_host_fatal_halt_is_terminal.restype = ctypes.c_uint32
        recovered.recovered_host_interrupt_ack_value.argtypes = [ctypes.c_uint32]
        recovered.recovered_host_interrupt_ack_value.restype = ctypes.c_uint32
        recovered.recovered_host_interrupt_rearm_control.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        recovered.recovered_host_interrupt_rearm_control.restype = ctypes.c_uint32
        recovered.recovered_host_timer_initial_value.restype = ctypes.c_uint32
        recovered.recovered_host_initial_interrupt_control.restype = ctypes.c_uint32
        class InitializePlan(ctypes.Structure):
            _fields_ = [("callback_target", ctypes.c_uint32),
                        ("g14_after", ctypes.c_uint32),
                        ("acknowledge_address", ctypes.c_uint32),
                        ("acknowledge_value", ctypes.c_uint32),
                        ("timer_addresses", ctypes.c_uint32 * 4),
                        ("timer_value", ctypes.c_uint32),
                        ("control_address", ctypes.c_uint32),
                        ("control_mmio_address", ctypes.c_uint32),
                        ("control_value", ctypes.c_uint32),
                        ("timer_state_address", ctypes.c_uint32),
                        ("timer_state_value", ctypes.c_uint32)]

        recovered.recovered_host_interrupt_initialize_plan.argtypes = [
            ctypes.POINTER(InitializePlan)]
        recovered.recovered_host_interrupt_initialize_plan.restype = ctypes.c_uint32
        initialize = InitializePlan()
        assert recovered.recovered_host_interrupt_initialize_plan(
            ctypes.byref(initialize)) == 1
        assert (initialize.callback_target, initialize.g14_after,
                initialize.acknowledge_address, initialize.acknowledge_value,
                list(initialize.timer_addresses), initialize.timer_value,
                initialize.control_address, initialize.control_mmio_address,
                initialize.control_value, initialize.timer_state_address,
                initialize.timer_state_value) == (
            0x1C10, 0, 0xE80000, 0,
            [0xF00004, 0xF00000, 0xF0000C, 0xF00008], 0x61A80,
            0x501CD0, 0xE80004, 0x23D, 0x51AAC0, 0)
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
        if recovered.recovered_host_fatal_halt_is_terminal() != 1:
            raise SystemExit("fatal halt is not marked terminal")

        expected_routes = {
            0x00000001: 1,
            0x00000002: 2,
            0x00000080: 0,
            0x00000200: 3,
            0x00000400: 4,
            0x00000800: 2,
        }
        dispatch = DispatchPlan()
        assert recovered.recovered_host_interrupt_dispatch_plan(
            0x400, 0xFFFFF523, ctypes.byref(dispatch)) == 1
        assert (dispatch.mask, dispatch.control_before, dispatch.control_after,
                dispatch.control_address, dispatch.control_mmio_address,
                dispatch.route) == (0x400, 0xFFFFF523, 0xFFFFF123,
                                    0x501CD0, 0xE80004, 4)
        update = MaskUpdatePlan()
        assert recovered.recovered_host_interrupt_mask_update_plan(
            8, 0xFFFFF523, ctypes.byref(update)) == 1
        assert (update.mask, update.control_before, update.control_cleared,
                update.control_rearmed, update.timer_address,
                update.timer_reset_value, update.timer_reload_value,
                update.timer_write_count, update.acknowledge_address,
                update.acknowledge_value) == (
            8, 0xFFFFF523, 0xFFFFF523, 0xFFFFF52B, 0xF00004, 0,
            0xFFFFF, 2, 0xE80000, 0xFFFFFFF7)
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

            expected_ack = (~mask) & 0xFFFFFFFF
            actual_ack = recovered.recovered_host_interrupt_ack_value(mask)
            if actual_ack != expected_ack:
                raise SystemExit(
                    f"interrupt ack mismatch mask=0x{mask:04x}: "
                    f"0x{actual_ack:08x} != 0x{expected_ack:08x}"
                )
            control = (mask * 0x9E3779B1) & 0xFFFFFFFF
            actual_control = recovered.recovered_host_interrupt_rearm_control(
                control, mask
            )
            expected_control = control | mask
            if actual_control != expected_control:
                raise SystemExit(
                    f"interrupt rearm mismatch mask=0x{mask:04x}: "
                    f"0x{actual_control:08x} != 0x{expected_control:08x}"
                    )

        listing = LISTING.read_text(encoding="utf-8")
        sequence = listing[listing.index("   1424:"):listing.index("   1438:")]
        for target in ("0x1c2c0", "0x29d50", "0xe2330", "0x29b20", "0x2cb0"):
            if f"call\t{target}" not in sequence:
                raise SystemExit(f"mask-1 device sequence missing call {target}")

    print(
        f"PASS: {vectors:,} host interrupt-mask vectors, "
        "65,536 dispatcher routes/acknowledgements, terminal fatal halt, and "
        "timer bootstrap constants"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
