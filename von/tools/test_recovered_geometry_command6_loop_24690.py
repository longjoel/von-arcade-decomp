#!/usr/bin/env python3
"""Validate routing and packet framing at i960 0x24690."""
import ctypes
import pathlib
import subprocess
import tempfile


MAINCPU = pathlib.Path(__file__).parents[1] / "build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("route", ctypes.c_uint32),
        ("initial_index", ctypes.c_uint32),
        ("iteration_limit", ctypes.c_uint32),
        ("active_mask", ctypes.c_uint32),
        ("active_packet_header", ctypes.c_uint32 * 2),
        ("fallback_packet_header", ctypes.c_uint32 * 2),
        ("packet_word_count_before_readback", ctypes.c_uint32),
        ("readback_address", ctypes.c_uint32),
        ("publish_address", ctypes.c_uint32),
        ("loop_increment", ctypes.c_uint32),
    ]


class Packet(ctypes.Structure):
    _fields_ = [("words", ctypes.c_uint32 * 6)]


maincpu = MAINCPU.read_text(encoding="utf-8")
for address, fragment in (
    ("240dc", "cvtir\tr6,fp0"),
    ("2428c", "shrdi\t1,r6,g4"),
    ("245d8", "cvtir\tr6,fp0"),
    ("246cc", "mov\t0,r4"),
    ("246d0", "lda\t0x4082c000,r5"),
    ("2479c", "movr\tg2,fp0"),
    ("247a0", "divrl\tr4,fp0,g6"),
    ("247a4", "movr\tr6,fp0"),
    ("247b0", "divrl\tr4,fp0,g6"),
    ("247cc", "st\tg0,0x884000"),
    ("247d4", "st\tg4,0x884000"),
    ("247dc", "st\tg3,0x884000"),
    ("247e4", "st\tr9,0x884000"),
    ("248cc", "movr\tg2,fp0"),
    ("248d0", "divrl\tr4,fp0,g6"),
    ("248d4", "movr\tr6,fp0"),
    ("248e0", "divrl\tr4,fp0,g6"),
    ("248fc", "st\tg0,0x884000"),
    ("24904", "st\tg4,0x884000"),
    ("24910", "st\tg3,0x884000"),
    ("24924", "st\tr9,0x884000"),
):
    line = next((line for line in maincpu.splitlines() if f"{address}:" in line), "")
    if fragment not in line:
        raise SystemExit(f"command-6 packet store {address} missing {fragment}")


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "command6.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_command6_loop_24690.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_command6_loop_plan
    build.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.POINTER(Plan)]
    active = lib.recovered_geometry_command6_active_iteration
    active.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    active.restype = ctypes.c_uint32
    packet = lib.recovered_geometry_command6_packet
    packet.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Packet)]
    packet_from_r6 = lib.recovered_geometry_command6_packet_from_r6_bits
    packet_from_r6.argtypes = [ctypes.c_uint32, ctypes.POINTER(Packet)]

    plan = Plan()
    build(-1, 7, 4, ctypes.byref(plan))
    assert (plan.route, plan.initial_index, plan.iteration_limit,
            plan.active_mask, list(plan.active_packet_header),
            list(plan.fallback_packet_header),
            plan.packet_word_count_before_readback,
            plan.readback_address, plan.publish_address,
            plan.loop_increment) == (
        0, 0, 7, 4, [5, 19], [5, 19], 6,
        0x802008, 0x801008, 1)

    build(0, 3, 0, ctypes.byref(plan))
    assert plan.route == 1
    assert active(0, 3, 4) == 1
    assert active(2, 3, 4) == 1
    assert active(3, 3, 4) == 0
    assert active(0, 3, 0) == 0
    assert active(0xffffffff, 3, 4) == 0

    packet_value = Packet()
    packet(0x12345678, 0x9abcdef0, ctypes.byref(packet_value))
    assert list(packet_value.words) == [5, 19, 0x12345678, 0x9abcdef0, 1, 58]
    packet_from_r6(0x40400000, ctypes.byref(packet_value))
    assert list(packet_value.words) == [5, 19, 0x3bda740e, 0x3ba3d70a, 1, 58]

print("PASS: 0x24690 command-6 loop routing")
