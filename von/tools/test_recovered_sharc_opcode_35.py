#!/usr/bin/env python3
"""Validate opcode 0x35's recovered stateful division contract."""

from __future__ import annotations

import ctypes
import re
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_35.c"


def bits(value: float) -> int:
    return struct.unpack("=I", struct.pack("=f", value))[0]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    table = re.search(
        r"recips_mantissa\[128\]\s*=\s*\{(.*?)\};", source, re.DOTALL
    )
    if table is None:
        raise SystemExit("recovered opcode-0x35 RECIPS table is missing")
    entries = re.findall(r"0x[0-9a-fA-F]+", table.group(1))
    if len(entries) != 128 or entries[49].lower() != "0x00390000":
        raise SystemExit(
            "recovered opcode-0x35 RECIPS table must contain 128 entries "
            "with 0x00390000 at index 49"
        )

    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode35.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        divide = ctypes.CDLL(str(library)).recovered_sharc_opcode_35_divide
        divide.argtypes = [ctypes.c_uint32] * 6
        divide.restype = ctypes.c_uint32

        assert divide(bits(2.0), bits(3.0), bits(4.0), bits(5.0), bits(6.0), bits(2.0)) == bits(16.0)
        assert divide(bits(-2.0), bits(3.0), bits(4.0), bits(5.0), bits(6.0), bits(-2.0)) == bits(-10.0)
        # The quotient lane must be rounded at each visible correction, as in
        # the ROM's F7/F12 schedule, to reproduce the live result.
        assert divide(bits(-64626.6171875), bits(1.0), bits(0.0), bits(1.0), bits(0.0), bits(-480.0079041)) == 0x4306A2F7
        assert divide(bits(1.0), bits(1.0), bits(0.0), bits(0.0), bits(0.0), bits(0.0)) == 0xffffffff
        assert divide(bits(1.0), bits(1.0), bits(0.0), bits(0.0), bits(0.0), bits(float("inf"))) == 0xffffffff

    print("PASS: SHARC opcode-0x35 stateful division model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
