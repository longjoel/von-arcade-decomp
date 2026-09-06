#!/usr/bin/env python3
"""Trace-validate the recovered 0x1dc90 block emitter against live writes.

The original 45-second no-input attract capture shows the emitter's inner
store (pc=0x1dcec) writing 38 tile halfwords: two 19-wide rows starting at
slot 0x0b29 (= row 44, column 41) with a +64 second row, every value
carrying the 0xc000 attribute. This test replays that geometry through the
compiled plan model and checks the observed offsets land exactly on the
planned grid with the planned attribute.
"""
import ctypes
import pathlib
import subprocess
import tempfile

# (offset, data) tile writes from the attract capture, in order.
OBSERVED = [
    "0b29 de80", "0b2a de81", "0b2b de82", "0b2c de83", "0b2d de82",
    "0b2e de84", "0b2f de85", "0b30 de86", "0b31 de87", "0b32 de88",
    "0b33 de89", "0b34 de8a", "0b35 de8b", "0b36 de8c", "0b37 de8d",
    "0b38 de8e", "0b39 de8f", "0b3a de90", "0b3b de83", "0b69 de91",
    "0b6a de92", "0b6b de93", "0b6c de94", "0b6d de95", "0b6e de96",
    "0b6f de97", "0b70 de98", "0b71 de99", "0b72 de9a", "0b73 de89",
    "0b74 de9b", "0b75 de9c", "0b76 de9d", "0b77 de9e", "0b78 de9f",
    "0b79 dea0", "0b7a dea1", "0b7b de94",
]


class Plan(ctypes.Structure):
    _fields_ = [
        ("row_addr", ctypes.c_uint32),
        ("col_addr", ctypes.c_uint32),
        ("plane_base", ctypes.c_uint32),
        ("glyph_attr", ctypes.c_uint32),
        ("row_stride_slots", ctypes.c_uint32),
        ("width", ctypes.c_uint32),
        ("rows", ctypes.c_uint32),
        ("total_halfwords", ctypes.c_uint32),
        ("start_slot", ctypes.c_uint32),
    ]


def main() -> None:
    pairs = [(int(tok[:4], 16), int(tok[5:], 16)) for tok in OBSERVED]
    assert len(pairs) == 38
    width, rows = 19, 2
    start = pairs[0][0]
    assert start == 0x0B29
    column, row = start % 64, start // 64

    with tempfile.TemporaryDirectory() as td:
        so = pathlib.Path(td) / "block-emit.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                        str(pathlib.Path(__file__).parents[1] / "i960" /
                            "recovered_block_emit_1dc90.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        plan_fn = lib.recovered_block_emit_plan
        plan_fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(width, rows, column, row, ctypes.byref(plan))

    assert plan.row_stride_slots == 64
    assert plan.glyph_attr == 0xC000
    assert plan.start_slot == start
    assert plan.total_halfwords == len(pairs)

    for index, (offset, data) in enumerate(pairs):
        expect = start + (index // width) * 64 + (index % width)
        assert offset == expect, f"write {index}: {offset:#x} != {expect:#x}"
        assert data & 0xC000 == 0xC000, f"write {index}: missing attribute"

    print("PASS: 0x1dc90 block emitter trace validation (38 tile writes)")


if __name__ == "__main__":
    main()
