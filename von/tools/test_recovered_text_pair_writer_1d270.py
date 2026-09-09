#!/usr/bin/env python3
"""Check the bounded two-row pair writer schedule at 0x1d270."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_pair_writer_1d270.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-text-pair-") as directory:
        library = Path(directory) / "text-pair.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
             "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))
        plan = recovered.recovered_text_pair_writer_plan
        pointers = [ctypes.POINTER(ctypes.c_uint32)] * 11
        plan.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(ctypes.c_uint16)] + pointers
        plan.restype = ctypes.c_uint32

        vectors = 0
        for value in (0x30, 0x31, 0x3f, 0x40, 0x12f):
            for row, column in ((0, 0), (4, 7), (46, 61), (0xffffffff, 62)):
                words = (ctypes.c_uint16 * 4)(0x0001, 0x7fff, 0x8000, 0xffff)
                outputs = [ctypes.c_uint32() for _ in range(11)]
                result = plan(value, row, column, words, *map(ctypes.byref, outputs))
                if result != 1:
                    raise SystemExit("pair writer did not produce a plan")
                selector, table_address = outputs[0].value, outputs[1].value
                tile = ((row << 6) + column) & 0xffffffff
                address = (0x01000000 + ((tile << 1) & 0xffffffff)) & 0xffffffff
                expected_selector = ((value - 0x30) & 0xffffffff) & 0xf
                if (selector, table_address) != (
                    expected_selector, 0x02ea1dd0 + expected_selector * 4):
                    raise SystemExit("pair table selection mismatch")
                expected_addresses = (address, address + 2, address + 0x80,
                                      address + 0x82)
                actual_addresses = (outputs[2].value, outputs[4].value,
                                    outputs[6].value, outputs[8].value)
                if actual_addresses != expected_addresses:
                    raise SystemExit("pair tile addresses mismatch")
                actual_values = (outputs[3].value, outputs[5].value,
                                 outputs[7].value, outputs[9].value)
                if actual_values != (
                    0x8001, 0xffff, 0x8000, 0xffff):
                    raise SystemExit("pair tile values mismatch")
                expected_column = column + 2 if column <= 61 else column
                if outputs[10].value != expected_column:
                    raise SystemExit("pair cursor update mismatch")
                vectors += 1

    print(f"PASS: {vectors} 0x1d270 two-row pair vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
