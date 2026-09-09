#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_row_input_84a04.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class RowInput(ctypes.Structure):
    _fields_ = ([(name, ctypes.c_uint32) for name in (
        "frame_byte_offset", "destination_offset")] +
        [(name, ctypes.c_int32) for name in (
            "source_0", "source_2", "source_4", "source_6", "source_a",
            "field_8c")])


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "frame-row-input.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_frame_row_input_84a04
    build.argtypes = [ctypes.c_uint32] * 3 + [ctypes.c_int32] * 6
    build.restype = RowInput

    result = build(0x30, 0x505060, 2, 1, 2, 3, 4, 5, 12)
    assert (result.frame_byte_offset, result.destination_offset,
            result.source_0, result.source_2, result.source_4,
            result.source_6, result.source_a, result.field_8c) == (
        0x30, 0x505180, 1, 2, 3, 4, 5, 192)
    signed = build(0, 0x505060, 0, -1, -2, -3, -4, -5, 70)
    assert (signed.source_0, signed.source_a, signed.field_8c) == (-1, -5, -40)

print("recovered 0x84a04 frame-row-input vectors: ok")

listing = [" ".join(line.split()).lower()
           for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
    ("84a04:", "ldos 0x5096a0(g4),g6"),
    ("84a14:", "ldos 0x2(g4)[r4],g5"),
    ("84a2c:", "ldos 0xa(g4)[r4],g1"),
    ("84a34:", "shlo 3,r6,g4"),
    ("84a3c:", "shlo 4,g4,g2"),
    ("84a70:", "stos g4,0x8c(g2)"),
):
    assert any(address in line and instruction in line for line in listing), (address, instruction)

print("recovered 0x84a04 frame-row-input listing evidence: ok")
