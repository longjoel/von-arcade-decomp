#!/usr/bin/env python3
"""Test the exact common gate before the 0xe2330 video jump table."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_video_dispatch.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("path", ctypes.c_int),
        ("bank_a", ctypes.c_uint32),
        ("table_index", ctypes.c_uint32),
    ]


class TilePlan(ctypes.Structure):
    _fields_ = [
        ("tile", ctypes.c_uint32 * 6),
        ("source", ctypes.c_uint32 * 6),
        ("count", ctypes.c_uint32),
    ]


class PlainTilePlan(ctypes.Structure):
    _fields_ = [
        ("tile", ctypes.c_uint32 * 9),
        ("source", ctypes.c_uint32 * 9),
        ("count", ctypes.c_uint32),
    ]


class ExitTilePlan(ctypes.Structure):
    _fields_ = [
        ("tile", ctypes.c_uint32 * 3),
        ("source", ctypes.c_uint32 * 3),
        ("count", ctypes.c_uint32),
        ("exit_address", ctypes.c_uint32),
    ]


class ConditionalPlainPlan(ctypes.Structure):
    _fields_ = [
        ("tile", ctypes.c_uint32 * 6),
        ("source", ctypes.c_uint32 * 6),
        ("count", ctypes.c_uint32),
        ("exit_address", ctypes.c_uint32),
    ]


class HelperTilePlan(ctypes.Structure):
    _fields_ = [
        ("tile", ctypes.c_uint32 * 6),
        ("source", ctypes.c_uint32 * 6),
        ("helper", ctypes.c_uint32),
        ("count", ctypes.c_uint32),
        ("exit_address", ctypes.c_uint32),
    ]


class LargeHelperTilePlan(ctypes.Structure):
    _fields_ = [
        ("tile", ctypes.c_uint32 * 9),
        ("source", ctypes.c_uint32 * 9),
        ("helper", ctypes.c_uint32),
        ("count", ctypes.c_uint32),
        ("exit_address", ctypes.c_uint32),
    ]


class MixedTilePlan(ctypes.Structure):
    _fields_ = [
        ("tile", ctypes.c_uint32 * 8),
        ("source", ctypes.c_uint32 * 8),
        ("helper", ctypes.c_uint32 * 8),
        ("count", ctypes.c_uint32),
        ("exit_address", ctypes.c_uint32),
    ]


class PostDispatchPlan(ctypes.Structure):
    _fields_ = [
        ("sentinel_match", ctypes.c_uint32),
        ("tile", ctypes.c_uint32 * 2),
        ("source", ctypes.c_uint32 * 2),
        ("helper", ctypes.c_uint32 * 2),
        ("count", ctypes.c_uint32),
        ("continuation", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-video-dispatch-") as directory:
        library = Path(directory) / "video-dispatch.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        function = recovered.recovered_video_dispatch_plan
        function.argtypes = [*(ctypes.c_uint32 for _ in range(6)), ctypes.POINTER(Plan)]
        function.restype = None

        arm0 = recovered.recovered_video_dispatch_arm0
        arm0.argtypes = [ctypes.POINTER(TilePlan)]
        arm0.restype = None

        for state, expected_path in ((0, 1), (0x81, 1), (0x82, 2), (0xFF, 0), (0x10000, 2)):
            plan = Plan()
            function(2, 1, 0, 7, 7, state, ctypes.byref(plan))
            if (plan.path, plan.bank_a, plan.table_index) != (expected_path, 1, state & 0xFFFFFFFF):
                raise SystemExit(f"gate mismatch at state 0x{state:x}")

        for values in ((0, 99, 99, 99, 99), (1, 2, 0, 0, 0), (2, 1, 0, 6, 7)):
            plan = Plan()
            function(*values, 0x40, ctypes.byref(plan))
            if plan.bank_a != int(values[0] == 0 or values == (2, 1, 0, 0, 0)):
                raise SystemExit(f"bank predicate mismatch for {values}")

        tiles = TilePlan()
        arm0(ctypes.byref(tiles))
        if list(tiles.tile[:4]) != [11, 21, 23, 25] or list(tiles.source[:4]) != [
            0x02FB75D0, 0x02FB5B90, 0x02FB5C50, 0x02FB5D10
        ] or tiles.count != 4:
            raise SystemExit("jump-table arm 0 mismatch")

        arm1 = recovered.recovered_video_dispatch_arm1
        arm1.argtypes = [ctypes.POINTER(TilePlan)]
        arm1.restype = None
        arm1(ctypes.byref(tiles))
        if list(tiles.tile) != [11, 21, 23, 25, 27, 29] or list(tiles.source) != [
            0x02FB75D0, 0x02FB5DD0, 0x02FB5E90,
            0x02FB5F50, 0x02FB6010, 0x02FB60D0
        ] or tiles.count != 6:
            raise SystemExit("jump-table arm 1 mismatch")

        arm2 = recovered.recovered_video_dispatch_arm2
        arm2.argtypes = [ctypes.POINTER(TilePlan)]
        arm2.restype = None
        arm2(ctypes.byref(tiles))
        if list(tiles.tile[:5]) != [11, 23, 25, 27, 29] or list(tiles.source[:5]) != [
            0x02FB75D0, 0x02FB6190, 0x02FB6250, 0x02FB6310, 0x02FB63D0
        ] or tiles.count != 5:
            raise SystemExit("jump-table arm 2 mismatch")

        arm3 = recovered.recovered_video_dispatch_arm3
        arm3.argtypes = [ctypes.POINTER(TilePlan)]
        arm3.restype = None
        arm3(ctypes.byref(tiles))
        if list(tiles.tile[:5]) != [11, 23, 25, 27, 29] or list(tiles.source[:5]) != [
            0x02FB75D0, 0x02FB6550, 0x02FB6610, 0x02FB66D0, 0x02FB6790
        ] or tiles.count != 5:
            raise SystemExit("jump-table arm 3 mismatch")

        arm4 = recovered.recovered_video_dispatch_arm4
        arm4.argtypes = [ctypes.POINTER(TilePlan)]
        arm4.restype = None
        arm4(ctypes.byref(tiles))
        if list(tiles.tile[:5]) != [11, 23, 25, 27, 29] or list(tiles.source[:5]) != [
            0x02FB75D0, 0x02FB6850, 0x02FB6910, 0x02FB69D0, 0x02FB6A90
        ] or tiles.count != 5:
            raise SystemExit("jump-table arm 4 mismatch")

        arm5 = recovered.recovered_video_dispatch_arm5
        arm5.argtypes = [ctypes.POINTER(TilePlan)]
        arm5.restype = None
        arm5(ctypes.byref(tiles))
        if list(tiles.tile[:3]) != [11, 27, 29] or list(tiles.source[:3]) != [
            0x02FB75D0, 0x02FB6B50, 0x02FB6C10
        ] or tiles.count != 3:
            raise SystemExit("jump-table arm 5 mismatch")

        arm6 = recovered.recovered_video_dispatch_arm6
        arm6.argtypes = [ctypes.POINTER(TilePlan)]
        arm6.restype = None
        arm6(ctypes.byref(tiles))
        if list(tiles.tile[:5]) != [11, 21, 23, 25, 27] or list(tiles.source[:5]) != [
            0x02FB75D0, 0x02FB6CD0, 0x02FB6D90, 0x02FB6E50, 0x02FB6F10
        ] or tiles.count != 5:
            raise SystemExit("jump-table arm 6 mismatch")

        arm7 = recovered.recovered_video_dispatch_arm7
        arm7.argtypes = [ctypes.POINTER(TilePlan)]
        arm7.restype = None
        arm7(ctypes.byref(tiles))
        if tiles.tile[0] != 11 or tiles.source[0] != 0x02FB75D0 or tiles.count != 1:
            raise SystemExit("jump-table arm 7 mismatch")

        arm8 = recovered.recovered_video_dispatch_arm8
        arm8.argtypes = [ctypes.POINTER(TilePlan)]
        arm8.restype = None
        arm8(ctypes.byref(tiles))
        if list(tiles.tile[:2]) != [11, 29] or list(tiles.source[:2]) != [
            0x02FB75D0, 0x02FB7450
        ] or tiles.count != 2:
            raise SystemExit("jump-table arm 8 mismatch")

        arm9 = recovered.recovered_video_dispatch_arm9
        arm9.argtypes = [ctypes.POINTER(TilePlan)]
        arm9.restype = None
        arm9(ctypes.byref(tiles))
        if list(tiles.tile[:4]) != [21, 25, 27, 29] or list(tiles.source[:4]) != [
            0x02FB6CD0, 0x02FB7E10, 0x02BFED8C, 0x02FB6FD0
        ] or tiles.count != 4:
            raise SystemExit("jump-table arm 9 mismatch")

        arm10 = recovered.recovered_video_dispatch_arm10
        arm10.argtypes = [ctypes.POINTER(PlainTilePlan)]
        arm10.restype = None
        plain = PlainTilePlan()
        arm10(ctypes.byref(plain))
        if list(plain.tile) != [11, 1, 3, 5, 7, 21, 25, 27, 29] or list(plain.source) != [
            0x02FB75D0, 0x02FB7A50, 0x02FB7B10, 0x02FB7BD0, 0x02FB7C90,
            0x02FB6CD0, 0x02FB7E10, 0x02BFED8C, 0x02FB6FD0
        ] or plain.count != 9:
            raise SystemExit("plain-expansion arm mismatch")

        arm11 = recovered.recovered_video_dispatch_arm11
        arm11.argtypes = [ctypes.POINTER(PlainTilePlan)]
        arm11.restype = None
        arm11(ctypes.byref(plain))
        if plain.tile[0] != 11 or plain.source[0] != 0x02FB75D0 or plain.count != 1:
            raise SystemExit("plain one-tile arm mismatch")

        arm12 = recovered.recovered_video_dispatch_arm12
        arm12.argtypes = [ctypes.POINTER(ExitTilePlan)]
        arm12.restype = None
        special = ExitTilePlan()
        arm12(ctypes.byref(special))
        if list(special.tile) != [23, 25, 27] or list(special.source) != [
            0x02FB8350, 0x02FB8410, 0x02FB84D0
        ] or special.count != 3 or special.exit_address != 0x000E33E4:
            raise SystemExit("special-exit mirrored arm mismatch")

        arm13 = recovered.recovered_video_dispatch_arm13
        arm13.argtypes = [ctypes.POINTER(TilePlan)]
        arm13.restype = None
        arm13(ctypes.byref(tiles))
        if list(tiles.tile[:5]) != [21, 23, 25, 27, 29] or list(tiles.source[:5]) != [
            0x02FB7F90, 0x02FB8050, 0x02FB8110, 0x02FB81D0, 0x02FB8290
        ] or tiles.count != 5:
            raise SystemExit("jump-table arm 13 mismatch")

        arm14 = recovered.recovered_video_dispatch_arm14
        arm14.argtypes = [ctypes.POINTER(PlainTilePlan)]
        arm14.restype = None
        arm14(ctypes.byref(plain))
        if list(plain.tile[:6]) != [1, 3, 5, 7, 9, 11] or list(plain.source[:6]) != [
            0x02FB7A50, 0x02FB7B10, 0x02FB4090, 0x02FB4150,
            0x02FB7BD0, 0x02FB7C90
        ] or plain.count != 6:
            raise SystemExit("plain shared-tail arm mismatch")

        arm15 = recovered.recovered_video_dispatch_arm15
        arm15.argtypes = [ctypes.POINTER(PlainTilePlan)]
        arm15.restype = None
        arm15(ctypes.byref(plain))
        if list(plain.tile[:4]) != [1, 3, 5, 7] or list(plain.source[:4]) != [
            0x02FB7A50, 0x02FB7B10, 0x02FB7BD0, 0x02FB7C90
        ] or plain.count != 4:
            raise SystemExit("plain short shared-tail arm mismatch")

        arm16 = recovered.recovered_video_dispatch_arm16
        arm16.argtypes = [ctypes.c_uint32, ctypes.POINTER(PlainTilePlan)]
        arm16.restype = None
        arm16(1, ctypes.byref(plain))
        if list(plain.tile[:2]) != [5, 7] or list(plain.source[:2]) != [
            0x02FB4990, 0x02FB4A50
        ] or plain.count != 2:
            raise SystemExit("bank-A conditional arm mismatch")
        arm16(0, ctypes.byref(plain))
        if list(plain.source[:2]) != [0x02FB4B10, 0x02FB4BD0] or plain.count != 2:
            raise SystemExit("bank-B conditional arm mismatch")

        arm17 = recovered.recovered_video_dispatch_arm17
        arm17.argtypes = [ctypes.c_uint32, ctypes.POINTER(PlainTilePlan)]
        arm17.restype = None
        arm17(1, ctypes.byref(plain))
        if list(plain.tile[:4]) != [9, 11, 1, 3] or list(plain.source[:4]) != [
            0x02FB5290, 0x02FB5350, 0x02FB3D90, 0x02FB3E50
        ] or plain.count != 4:
            raise SystemExit("bank-A four-tile arm mismatch")
        arm17(0, ctypes.byref(plain))
        if list(plain.source[:4]) != [
            0x02FB5410, 0x02FB54D0, 0x02FB3F10, 0x02FB3FD0
        ] or plain.count != 4:
            raise SystemExit("bank-B four-tile arm mismatch")

        arm18 = recovered.recovered_video_dispatch_arm18
        arm18.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm18.restype = None
        conditional = ConditionalPlainPlan()
        arm18(1, ctypes.byref(conditional))
        if list(conditional.tile) != [1, 3, 5, 7, 9, 11] or list(conditional.source) != [
            0x02FB3D90, 0x02FB3E50, 0x02FB4990,
            0x02FB4A50, 0x02FB4C90, 0x02FB5350
        ] or conditional.count != 6 or conditional.exit_address != 0x000E30A8:
            raise SystemExit("bank-A six-tile arm mismatch")
        arm18(0, ctypes.byref(conditional))
        if list(conditional.source) != [
            0x02FB3F10, 0x02FB3FD0, 0x02FB4B10,
            0x02FB4BD0, 0x02FB4E10, 0x02FB4ED0
        ] or conditional.exit_address != 0x000E30CC:
            raise SystemExit("bank-B six-tile arm mismatch")

        arm19 = recovered.recovered_video_dispatch_arm19
        arm19.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm19.restype = None
        arm19(1, ctypes.byref(conditional))
        if list(conditional.tile[:4]) != [5, 7, 9, 11] or list(conditional.source[:4]) != [
            0x02FB4990, 0x02FB4A50, 0x02FB4C90, 0x02FB4D50
        ] or conditional.count != 4 or conditional.exit_address != 0x000E2F24:
            raise SystemExit("bank-A four-tile conditional arm mismatch")
        arm19(0, ctypes.byref(conditional))
        if list(conditional.source[:4]) != [
            0x02FB4B10, 0x02FB4BD0, 0x02FB4E10, 0x02FB4ED0
        ] or conditional.exit_address != 0x000E2F48:
            raise SystemExit("bank-B four-tile conditional arm mismatch")

        arm20 = recovered.recovered_video_dispatch_arm20
        arm20.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm20.restype = None
        arm20(1, ctypes.byref(conditional))
        if list(conditional.tile[:4]) != [9, 11, 1, 3] or list(conditional.source[:4]) != [
            0x02FB4C90, 0x02FB4D50, 0x02FB4390, 0x02FB4450
        ] or conditional.count != 4 or conditional.exit_address != 0x000E2F70:
            raise SystemExit("bank-A e2c14 arm mismatch")
        arm20(0, ctypes.byref(conditional))
        if list(conditional.source[:4]) != [
            0x02FB4E10, 0x02FB4ED0, 0x02FB4510, 0x02FB45D0
        ] or conditional.exit_address != 0x000E2F94:
            raise SystemExit("bank-B e2c14 arm mismatch")

        arm21 = recovered.recovered_video_dispatch_arm21
        arm21.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm21.restype = None
        arm21(1, ctypes.byref(conditional))
        if list(conditional.tile[:4]) != [1, 3, 5, 7] or list(conditional.source[:4]) != [
            0x02FB4390, 0x02FB4450, 0x02FB4090, 0x02FB4150
        ] or conditional.count != 4 or conditional.exit_address != 0x000E2FBC:
            raise SystemExit("bank-A e2ca0 arm mismatch")
        arm21(0, ctypes.byref(conditional))
        if list(conditional.source[:4]) != [
            0x02FB4510, 0x02FB45D0, 0x02FB4210, 0x02FB42D0
        ] or conditional.exit_address != 0x000E2FE0:
            raise SystemExit("bank-B e2ca0 arm mismatch")

        arm22 = recovered.recovered_video_dispatch_arm22
        arm22.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm22.restype = None
        arm22(1, ctypes.byref(conditional))
        if list(conditional.tile) != [5, 7, 9, 11, 13, 15] or list(conditional.source) != [
            0x02FB4090, 0x02FB4150, 0x02FB5290,
            0x02FB5350, 0x02FB4F90, 0x02FB5050
        ] or conditional.count != 6 or conditional.exit_address != 0x000E33F4:
            raise SystemExit("bank-A e2d2c arm mismatch")
        arm22(0, ctypes.byref(conditional))
        if list(conditional.source) != [
            0x02FB4210, 0x02FB42D0, 0x02FB5410,
            0x02FB54D0, 0x02FB5110, 0x02FB51D0
        ] or conditional.exit_address != 0x000E33F4:
            raise SystemExit("bank-B e2d2c arm mismatch")

        arm23 = recovered.recovered_video_dispatch_arm23
        arm23.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm23.restype = None
        arm23(1, ctypes.byref(conditional))
        if list(conditional.tile[:2]) != [9, 11] or list(conditional.source[:2]) != [
            0x02FB5290, 0x02FB5350
        ] or conditional.count != 2 or conditional.exit_address != 0x000E3008:
            raise SystemExit("bank-A e2df8 arm mismatch")
        arm23(0, ctypes.byref(conditional))
        if list(conditional.source[:2]) != [0x02FB5410, 0x02FB54D0] or conditional.exit_address != 0x000E304C:
            raise SystemExit("bank-B e2df8 arm mismatch")

        arm24 = recovered.recovered_video_dispatch_arm24
        arm24.argtypes = [ctypes.c_uint32]
        arm24.restype = ctypes.c_uint32
        if arm24(1) != 0x000E3008 or arm24(0) != 0x000E304C:
            raise SystemExit("e2e44 bank gate mismatch")

        arm25 = recovered.recovered_video_dispatch_arm25
        arm25.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm25.restype = None
        arm25(1, ctypes.byref(conditional))
        if list(conditional.tile[:2]) != [1, 3] or list(conditional.source[:2]) != [
            0x02FB3D90, 0x02FB3E50
        ] or conditional.count != 2 or conditional.exit_address != 0x000E33F4:
            raise SystemExit("bank-A e2e4c payload mismatch")
        arm25(0, ctypes.byref(conditional))
        if list(conditional.source[:2]) != [0x02FB3F10, 0x02FB3FD0] or conditional.count != 2:
            raise SystemExit("bank-B e2e4c payload mismatch")

        arm26 = recovered.recovered_video_dispatch_arm26
        arm26.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm26.restype = None
        arm26(1, ctypes.byref(conditional))
        if list(conditional.tile[:2]) != [5, 7] or list(conditional.source[:2]) != [
            0x02FB4990, 0x02FB4A50
        ] or conditional.count != 2 or conditional.exit_address != 0x000E33F4:
            raise SystemExit("bank-A e2ea0 payload mismatch")
        arm26(0, ctypes.byref(conditional))
        if list(conditional.source[:2]) != [0x02FB4B10, 0x02FB4BD0] or conditional.count != 2:
            raise SystemExit("bank-B e2ea0 payload mismatch")

        arm27 = recovered.recovered_video_dispatch_arm27
        arm27.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm27.restype = None
        arm27(1, ctypes.byref(conditional))
        if list(conditional.tile[:2]) != [9, 11] or list(conditional.source[:2]) != [
            0x02FB4C90, 0x02FB4D50
        ] or conditional.count != 2 or conditional.exit_address != 0x000E30A8:
            raise SystemExit("bank-A e2eec payload mismatch")
        arm27(0, ctypes.byref(conditional))
        if list(conditional.source[:2]) != [0x02FB4E10, 0x02FB4ED0] or conditional.exit_address != 0x000E30CC:
            raise SystemExit("bank-B e2eec payload mismatch")

        arm28 = recovered.recovered_video_dispatch_arm28
        arm28.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm28.restype = None
        arm28(1, ctypes.byref(conditional))
        if list(conditional.tile[:4]) != [1, 3, 5, 7] or list(conditional.source[:4]) != [
            0x02FB4F90, 0x02FB5050, 0x02FB4690, 0x02FB4750
        ] or conditional.count != 4 or conditional.exit_address != 0x000E33F4:
            raise SystemExit("bank-A e3004 payload mismatch")
        arm28(0, ctypes.byref(conditional))
        if list(conditional.source[:4]) != [
            0x02FB5110, 0x02FB51D0, 0x02FB4810, 0x02FB48D0
        ] or conditional.count != 4:
            raise SystemExit("bank-B e3004 payload mismatch")

        arm29 = recovered.recovered_video_dispatch_arm29
        arm29.argtypes = [ctypes.c_uint32, ctypes.POINTER(ConditionalPlainPlan)]
        arm29.restype = None
        arm29(1, ctypes.byref(conditional))
        if list(conditional.tile[:2]) != [1, 3] or list(conditional.source[:2]) != [
            0x02FB4C90, 0x02FB4D50
        ] or conditional.count != 2 or conditional.exit_address != 0x000E33F4:
            raise SystemExit("bank-A e3090 payload mismatch")
        arm29(0, ctypes.byref(conditional))
        if list(conditional.source[:2]) != [0x02FB4E10, 0x02FB4ED0] or conditional.count != 2:
            raise SystemExit("bank-B e3090 payload mismatch")

        arm30 = recovered.recovered_video_dispatch_arm30
        arm30.argtypes = [ctypes.POINTER(TilePlan)]
        arm30.restype = None
        arm30(ctypes.byref(tiles))
        if list(tiles.tile[:5]) != [21, 23, 25, 27, 29] or list(tiles.source[:5]) != [
            0x00577598, 0x0057759C, 0x005775A0, 0x005775A4, 0x005775A8
        ] or tiles.count != 5:
            raise SystemExit("e30dc mirrored pointer-table arm mismatch")

        arm32 = recovered.recovered_video_dispatch_arm32
        arm32.argtypes = [ctypes.POINTER(TilePlan)]
        arm32.restype = None
        arm32(ctypes.byref(tiles))
        if list(tiles.tile[:1]) != [3] or list(tiles.source[:1]) != [0x02FB7D50] or tiles.count != 1:
            raise SystemExit("e3130 immediate-branch arm mismatch")

        large_helper_plan = LargeHelperTilePlan()
        arm33 = recovered.recovered_video_dispatch_arm33
        arm33.argtypes = [ctypes.c_uint32, ctypes.POINTER(LargeHelperTilePlan)]
        arm33.restype = None
        arm33(1, ctypes.byref(large_helper_plan))
        if list(large_helper_plan.tile[:8]) != [1, 3, 5, 7, 21, 25, 27, 29] or list(large_helper_plan.source[:8]) != [
            0x02FB3D90, 0x02FB3E50, 0x02FB4990, 0x02FB4A50,
            0x02FB6CD0, 0x02FB7E10, 0x02BFED8C, 0x02FB6FD0,
        ] or large_helper_plan.helper != 0x000E1FB0 or large_helper_plan.count != 8 or large_helper_plan.exit_address != 0x000E33F4:
            raise SystemExit("bank-A e3248 e1fb0 arm mismatch")
        arm33(0, ctypes.byref(large_helper_plan))
        if list(large_helper_plan.source[:8]) != [
            0x02FB3F10, 0x02FB3FD0, 0x02FB4B10, 0x02FB4BD0,
            0x02FB6CD0, 0x02FB7E10, 0x02BFED8C, 0x02FB6FD0,
        ] or large_helper_plan.count != 8:
            raise SystemExit("bank-B e3248 e1fb0 arm mismatch")

        helper_plan = HelperTilePlan()
        arm34 = recovered.recovered_video_dispatch_arm34
        arm34.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(HelperTilePlan)]
        arm34.restype = None
        arm34(1, 6, ctypes.byref(helper_plan))
        if list(helper_plan.tile[:2]) != [1, 3] or list(helper_plan.source[:2]) != [
            0x00142F94, 0x00142F98
        ] or helper_plan.helper != 0x000E1FB0 or helper_plan.count != 2 or helper_plan.exit_address != 0x000E33F4:
            raise SystemExit("bank-A e319c selector arm mismatch")
        arm34(0, 6, ctypes.byref(helper_plan))
        if list(helper_plan.tile[:2]) != [1, 3] or list(helper_plan.source[:2]) != [
            0x00142F98, 0x00142FA0
        ] or helper_plan.count != 2:
            raise SystemExit("bank-B e319c normal selector arm mismatch")
        arm34(0, 5, ctypes.byref(helper_plan))
        if list(helper_plan.tile[:2]) != [5, 7] or list(helper_plan.source[:2]) != [
            0x00142F8C, 0x00142F90
        ] or helper_plan.count != 2:
            raise SystemExit("bank-B e319c selector-5 arm mismatch")

        mixed_plan = MixedTilePlan()
        arm35 = recovered.recovered_video_dispatch_arm35
        arm35.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(MixedTilePlan)]
        arm35.restype = None
        arm35(1, 6, ctypes.byref(mixed_plan))
        if list(mixed_plan.tile[:5]) != [1, 3, 25, 27, 29] or list(mixed_plan.source[:5]) != [
            0x00142EF4, 0x00142EF8, 0x00143704, 0x001437C4, 0x02FB8590
        ] or list(mixed_plan.helper[:5]) != [0x000E1FB0, 0x000E1FB0, 0x000E2040, 0x000E2040, 0x000E2040] or mixed_plan.count != 5 or mixed_plan.exit_address != 0x000E33F4:
            raise SystemExit("bank-A e3314 mixed arm mismatch")
        arm35(0, 5, ctypes.byref(mixed_plan))
        if list(mixed_plan.tile[:5]) != [5, 7, 25, 27, 29] or list(mixed_plan.source[:5]) != [
            0x00142F8C, 0x00142F90, 0x00143704, 0x001437C4, 0x02FB8590
        ] or mixed_plan.count != 5:
            raise SystemExit("bank-B e3314 selector-5 mixed arm mismatch")

        post_plan = PostDispatchPlan()
        arm36 = recovered.recovered_video_dispatch_arm36
        arm36.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(PostDispatchPlan)]
        arm36.restype = None
        arm36(0x200, 1, ctypes.byref(post_plan))
        if post_plan.sentinel_match != 1 or list(post_plan.tile) != [5, 7] or list(post_plan.source) != [
            0x02FB5890, 0x02FB5950
        ] or list(post_plan.helper) != [0x000E2040, 0x000E2040] or post_plan.count != 2 or post_plan.continuation != 0x000E35A0:
            raise SystemExit("e33f4 bank-A sentinel subpath mismatch")
        arm36(0x200, 0, ctypes.byref(post_plan))
        if list(post_plan.tile) != [1, 3] or post_plan.count != 2:
            raise SystemExit("e33f4 bank-B sentinel subpath mismatch")
        arm36(0x201, 1, ctypes.byref(post_plan))
        if post_plan.sentinel_match != 0 or post_plan.count != 0 or post_plan.continuation != 0x000E3444:
            raise SystemExit("e33f4 nonmatching sentinel gate mismatch")

        arm37 = recovered.recovered_video_dispatch_arm37
        arm37.argtypes = [ctypes.c_uint32, ctypes.POINTER(PostDispatchPlan)]
        arm37.restype = None
        arm37(1, ctypes.byref(post_plan))
        if post_plan.sentinel_match != 1 or list(post_plan.tile) != [5, 7] or list(post_plan.source) != [
            0x02FB5A10, 0x02FB5AD0
        ] or list(post_plan.helper) != [0x000E2040, 0x000E2040] or post_plan.count != 2 or post_plan.continuation != 0x000E35A0:
            raise SystemExit("e349c bank-A sentinel arm mismatch")
        arm37(0, ctypes.byref(post_plan))
        if list(post_plan.tile) != [1, 3] or post_plan.count != 2:
            raise SystemExit("e349c bank-B sentinel arm mismatch")

        arm38 = recovered.recovered_video_dispatch_arm38
        arm38.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(PostDispatchPlan)]
        arm38.restype = None
        arm38(0x410, 1, ctypes.byref(post_plan))
        if list(post_plan.tile) != [5, 7] or list(post_plan.source) != [
            0x02BFE584, 0x02BFE604
        ] or list(post_plan.helper) != [0x000E2040, 0x000E2040] or post_plan.count != 2 or post_plan.continuation != 0x000E35A0:
            raise SystemExit("e34e4 bank-A indexed arm mismatch")
        arm38(0x410, 0, ctypes.byref(post_plan))
        if list(post_plan.tile) != [1, 3] or post_plan.count != 2:
            raise SystemExit("e34e4 bank-B indexed arm mismatch")

        arm39 = recovered.recovered_video_dispatch_arm39
        arm39.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(PostDispatchPlan)]
        arm39.restype = None
        arm39(0x430, 1, ctypes.byref(post_plan))
        if list(post_plan.tile) != [5, 7] or list(post_plan.source) != [
            0x02BFE684, 0x02BFE704
        ] or list(post_plan.helper) != [0x000E2040, 0x000E2040] or post_plan.count != 2 or post_plan.continuation != 0x000E35A0:
            raise SystemExit("e353c bank-A indexed arm mismatch")
        arm39(0x430, 0, ctypes.byref(post_plan))
        if list(post_plan.tile) != [1, 3] or post_plan.count != 2:
            raise SystemExit("e353c bank-B indexed arm mismatch")

        terminal_reset = recovered.recovered_video_dispatch_terminal_reset
        terminal_reset.argtypes = []
        terminal_reset.restype = ctypes.c_uint32
        if terminal_reset() != 0x000000FF:
            raise SystemExit("e35a0 sentinel reset mismatch")

        post_route = recovered.recovered_video_dispatch_post_route
        post_route.argtypes = [ctypes.c_uint32]
        post_route.restype = ctypes.c_int
        route_cases = {
            0x00000200: 0,
            0x0000021D: 0,
            0x0000021E: 4,
            0x0000021F: 1,
            0x00000220: 4,
            0x000003FF: 4,
            0x00000400: 2,
            0x0000041E: 2,
            0x0000041F: 4,
            0x00000420: 3,
            0x0000043F: 3,
            0x00000440: 4,
        }
        for sentinel, expected_route in route_cases.items():
            if post_route(sentinel) != expected_route:
                raise SystemExit(f"e3444 route mismatch at sentinel 0x{sentinel:x}")

        arm40 = recovered.recovered_video_dispatch_arm40
        arm40.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(PostDispatchPlan)]
        arm40.restype = None
        arm40(0x10, 1, ctypes.byref(post_plan))
        if list(post_plan.tile) != [5, 7] or list(post_plan.source) != [
            0x00129E68, 0x00129EE8
        ] or list(post_plan.helper) != [0x000E2040, 0x000E2040] or post_plan.count != 2 or post_plan.continuation != 0x000E35A0:
            raise SystemExit("e3444 lower-range bank-A arm mismatch")
        arm40(0x10, 0, ctypes.byref(post_plan))
        if list(post_plan.tile) != [1, 3] or post_plan.count != 2:
            raise SystemExit("e3444 lower-range bank-B arm mismatch")

        arm31 = recovered.recovered_video_dispatch_arm31
        arm31.argtypes = [ctypes.POINTER(HelperTilePlan)]
        arm31.restype = None
        arm31(ctypes.byref(helper_plan))
        if list(helper_plan.tile[:5]) != [21, 23, 25, 27, 29] or list(helper_plan.source[:5]) != [
            0x02FB3D90, 0x00142DD4, 0x02FA5AD0, 0x02FABB90, 0x02FB1C50
        ] or helper_plan.helper != 0x000E1FB0 or helper_plan.count != 5 or helper_plan.exit_address != 0x000E33F4:
            raise SystemExit("e314c e1fb0 arm mismatch")

    print("PASS: 0xe2330 bank flag, sentinel gate, bounds, and arms 0-40")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
