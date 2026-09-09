#!/usr/bin/env python3
"""Validate the bounded transform-route model at 0x2d9a0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_transform_dispatch_2d9a0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("profile_helper", ctypes.c_uint32),
        ("service_helper", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32),
        ("packet_selectors", ctypes.c_uint32 * 10),
        ("packet_selector_count", ctypes.c_uint32),
        ("state_address", ctypes.c_uint32 * 7),
        ("state_store_width", ctypes.c_uint32 * 7),
        ("state_write_count", ctypes.c_uint32),
        ("continuation", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "geometry-transform.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    plan_function = recovered.recovered_geometry_transform_dispatch_plan
    plan_function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    plan_function(ctypes.byref(plan))

    assert (plan.profile_helper, plan.service_helper, plan.fifo_address,
            plan.packet_selector_count, plan.state_write_count,
            plan.continuation) == (0x295d0, 0x2a990, 0x884000, 10, 7, 0x2dc40)
    assert list(plan.packet_selectors) == [8, 16, 10, 31, 29, 30, 10, 20, 21, 18]
    assert list(plan.state_address) == [0x51aad0, 0x51aad2, 0x51aad4,
                                        0x51aad8, 0x51aadc, 0x51aae0,
                                        0x51aae4]
    assert list(plan.state_store_width) == [2, 2, 2, 4, 4, 4, 4]

    low_halfword = recovered.recovered_geometry_transform_low_halfword
    low_halfword.argtypes = [ctypes.c_uint32]
    low_halfword.restype = ctypes.c_uint32
    toggle_sign = recovered.recovered_geometry_transform_toggle_sign_bit
    toggle_sign.argtypes = [ctypes.c_uint32]
    toggle_sign.restype = ctypes.c_uint32
    assert low_halfword(0x1234abcd) == 0xabcd
    assert toggle_sign(0x01234567) == 0x81234567
    state_values = recovered.recovered_geometry_transform_state_values
    state_values.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(ctypes.c_uint32)]
    values = (ctypes.c_uint32 * 6)()
    state_values(0x81234567, 0x11111111, 0x22222222,
                 0x33333333, 0x44444444, values)
    assert list(values) == [0x81234567, 0, 0, 0x11111111,
                            0x22222222, 0x33333333]
    final_state = recovered.recovered_geometry_transform_final_state_value
    final_state.argtypes = [ctypes.c_uint32]
    final_state.restype = ctypes.c_uint32
    assert final_state(0x44444444) == 0x44444444

    listing = LISTING.read_text(encoding="utf-8")
    block_start = listing.index("   2d9a0:")
    block_end = listing.index("   2dc40:") + 80
    block = listing[block_start:block_end]
    for evidence in (
            "call\t0x295d0", "call\t0x2a990", "st\tr9,0x884000",
            "mov\t31,r8", "mov\t29,r9", "mov\t30,r8",
            "mov\t20,r9", "mov\t21,r8", "mov\t18,r9",
            "stos\tr4,0x51aad0", "st\tg1,0x51aad8",
            "st\tg13,0x51aadc", "st\tg2,0x51aae0",
            "st\tg6,0x51aae4", "ret"):
        if evidence not in block:
            raise AssertionError(f"transform listing evidence missing: {evidence}")

print("PASS: 0x2d9a0 geometry transform dispatch")
