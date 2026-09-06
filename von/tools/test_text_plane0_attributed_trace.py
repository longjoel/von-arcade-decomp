#!/usr/bin/env python3
"""Trace-validate the 0x1dd10 attributed block writer against live writes.

Same 38-write attract burst as the 0x1dc90 schedule check (pc=0x1dcec sits
inside 0x1dd10-0x1dd40): two 19-wide rows at explicit origin column 41,
row 44, +64 row stride, every value carrying forced 0xc000 attributes.
This test replays all 38 cells through the compiled explicit-origin plan:
destination addresses must match the observed slots exactly, and stripping
0xc000 from each observed value must yield a source word that re-masks to
the observed value (round-trip consistency for the attribute contract).
"""
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_plane0_attributed_block.c"

# (offset, data) tile writes from the attract capture, in order. Shared
# provenance with test_block_emit_1dc90_trace.py; duplicated so each test
# stays self-contained.
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

COLUMN, ROW, WIDTH, HEIGHT = 41, 44, 19, 2


class Cell(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source_byte_offset", "destination_byte_address", "source_word_or_mask")]


def main() -> int:
    pairs = [(int(tok[:4], 16), int(tok[5:], 16)) for tok in OBSERVED]
    assert len(pairs) == WIDTH * HEIGHT
    with tempfile.TemporaryDirectory(prefix="von-attributed-trace-") as directory:
        library = Path(directory) / "attributed-block.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_plane0_attributed_cell_plan
        plan_fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Cell)]
        plan_fn.restype = ctypes.c_uint32
        cell = Cell()
        for index, (offset, data) in enumerate(pairs):
            y, x = divmod(index, WIDTH)
            source_word = data & ~0xC000
            assert plan_fn(COLUMN, ROW, WIDTH, HEIGHT, y, x,
                           source_word, ctypes.byref(cell)) == 1
            assert (cell.destination_byte_address - 0x01000000) // 2 == offset, \
                f"cell {(y, x)}: plan slot != observed {offset:#x}"
            assert cell.source_byte_offset == ((y * WIDTH) + x) << 1
            assert cell.source_word_or_mask == data, \
                f"cell {(y, x)}: re-masked source != observed"
            assert data & 0xC000 == 0xC000

    print("PASS: 0x1dd10 attributed block trace replay (38 tile writes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
