#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_alternate_row_scan_84f10.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Scan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "success_85058", "returns_after_scan", "selected_row", "scanned_rows")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "alternate-scan.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_alternate_row_scan_84f10
    words = ctypes.c_uint32 * 8
    build.argtypes = [words, words, words]
    build.restype = Scan

    fields = words(60, 60, 60, 60, 60, 60, 60, 60)
    globals_ = words(0, 1, 1, 0, 0, 0, 0, 0)
    counts = words(1, 1, 3, 0, 0, 0, 0, 0)
    result = build(fields, globals_, counts)
    assert (result.success_85058, result.returns_after_scan,
            result.selected_row, result.scanned_rows) == (1, 0, 2, 3)

    result = build(words(*([49] * 8)), words(*([1] * 8)),
                   words(*([3] * 8)))
    assert (result.success_85058, result.returns_after_scan,
            result.selected_row, result.scanned_rows) == (0, 1, 0xffffffff, 8)

    result = build(words(*([50] * 8)), words(*([1] * 8)),
                   words(*([1] * 8)))
    assert (result.success_85058, result.returns_after_scan,
            result.selected_row, result.scanned_rows) == (0, 1, 0xffffffff, 8)

    terminal_fields = words(49, 49, 49, 49, 49, 49, 49, 60)
    terminal_globals = words(0, 0, 0, 0, 0, 0, 0, 1)
    terminal_counts = words(1, 1, 1, 1, 1, 1, 1, 3)
    result = build(terminal_fields, terminal_globals, terminal_counts)
    assert (result.success_85058, result.selected_row,
            result.scanned_rows) == (1, 7, 8)

print("recovered 0x84f10 alternate-row-scan vectors: ok")

listing = [" ".join(line.split()).lower()
           for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
    ("84f10:", "mov 0,g13"),
    ("84f14:", "shro 16,r8,r6"),
    ("84f68:", "ldos 0x7c(g7),g4"),
    ("85034:", "cmpibge 1,g6,0x8503c"),
    ("8503c:", "addo g13,1,g13"),
    ("85040:", "cmpi 7,g13"),
    ("85048:", "lda 0x90(g3),g3"),
):
    assert any(address in line and instruction in line for line in listing), (address, instruction)

print("recovered 0x84f10 alternate-row-scan listing evidence: ok")
