#!/usr/bin/env python3
"""Validate the bounded object initializer recovered from i960 0x27550-0x27c50."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_initializer_27550.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

OBJECT_SIZE = 0x600
SENTINEL = 0xAA

CONFIG = 0xA1B2C3D4
CALLBACK = 0x11223344
RELATED = 0x55667788
KIND = 0x00000009
TEAM = 0xDEADBEEF
X = 0x00001234
Z = 0x00005678
FACING = 0x9ABC

# Fields the bounded initializer writes with a zero halfword (0x2755c-0x2769c).
ZERO_HALFWORDS = (0x00, 0x172, 0x174, 0x176, 0x178, 0x17a, 0x17c, 0x17e,
                  0x2c, 0x2e, 0x32, 0x34, 0x36, 0x38, 0x3a, 0x1b2,
                  0x1ea, 0x1ec, 0x1ee, 0x1f0)

# Bytes the bounded initializer zeroes.
ZERO_BYTES = (0x1ab, 0x1ac, 0x1ad, 0x1b0, 0x1b1)

# Offsets outside the modeled field set that must survive the call.
UNTOUCHED = (0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b,
             0x20, 0x22, 0x24, 0x26, 0x28, 0x2a,
             0x50, 0x54, 0x58, 0x5c, 0x60,
             0x70, 0x71, 0x72, 0x73, 0x78, 0x79, 0x7a, 0x7b,
             0x90, 0x94, 0x200, 0x204, 0x300, 0x400, 0x500, 0x5f0, 0x5fe,
             0x5ff)

# (address, mnemonic, operand) taken verbatim from 0x27550-0x276d4.
BLOCK_EVIDENCE = (
    (0x27558, "st", "g6,0x6c(g0)"),
    (0x2755c, "stos", "g14,(g0)"),
    (0x27564, "stos", "g13,0x2(g0)"),
    (0x27568, "st", "g1,0x74(g0)"),
    (0x2756c, "st", "g3,0x64(g0)"),
    (0x27570, "st", "g5,0x68(g0)"),
    (0x27574, "stos", "g14,0x172(g0)"),
    (0x27578, "stos", "g13,0x170(g0)"),
    (0x2758c, "stos", "g14,0x174(g0)"),
    (0x2759c, "stos", "g14,0x176(g0)"),
    (0x275a8, "stos", "g14,0x178(g0)"),
    (0x275b4, "stos", "g14,0x17a(g0)"),
    (0x275c0, "stos", "g14,0x17c(g0)"),
    (0x275cc, "stos", "g14,0x17e(g0)"),
    (0x27600, "st", "g13,0x4(g0)"),
    (0x27670, "st", "r7,0x8(r4)"),
    (0x27674, "st", "g8,0x10(r4)"),
    (0x27688, "stos", "g14,0x2e(r4)"),
    (0x2769c, "stos", "g14,0x3a(r4)"),
    (0x276c4, "stos", "g13,0x46(r4)"),
    (0x276d0, "st", "g4,0x1cc(r4)"),
    (0x276d4, "st", "g4,0x1c8(r4)"),
)

# Later writes that pin the corrected constants and widths.
TAIL_EVIDENCE = (
    (0x277ec, "stos", "g9,0x184(r4)"),
    (0x27814, "stob", "g14,0x1ad(r4)"),
    (0x27818, "stob", "g14,0x1ac(r4)"),
    (0x2781c, "stob", "g14,0x1ab(r4)"),
    (0x2784c, "stos", "g14,0x1b2(r4)"),
    (0x27850, "stob", "g14,0x1b1(r4)"),
    (0x27854, "stob", "g14,0x1b0(r4)"),
    (0x2787c, "stos", "g4,0x1e8(r4)"),
    (0x27880, "stos", "g4,0x1e6(r4)"),
    (0x27884, "stos", "g4,0x1e4(r4)"),
    (0x27888, "stos", "g4,0x1e2(r4)"),
    (0x2788c, "stos", "g14,0x1f0(r4)"),
    (0x27890, "stos", "g14,0x1ee(r4)"),
    (0x27894, "stos", "g14,0x1ec(r4)"),
    (0x27898, "stos", "g14,0x1ea(r4)"),
    (0x278a4, "stos", "r6,0x1fa(r4)"),
    (0x278a8, "stos", "r6,0x1f8(r4)"),
    (0x278ac, "lda", "0xff,g13"),
    (0x278b0, "stos", "g13,0x1fc(r4)"),
)


def u16(buf, offset):
    return ctypes.c_uint16.from_buffer(buf, offset).value


def u32(buf, offset):
    return ctypes.c_uint32.from_buffer(buf, offset).value


def load_evidence():
    table = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts or not parts[0].endswith(":"):
            continue
        try:
            address = int(parts[0][:-1], 16)
        except ValueError:
            continue
        table[address] = parts
    return table


def check_evidence(table, wanted):
    for address, mnemonic, operand in wanted:
        parts = table.get(address)
        if parts is None:
            raise AssertionError(f"listing address missing: {address:#x}")
        if parts[5:] != [mnemonic, operand]:
            raise AssertionError(
                f"listing evidence mismatch at {address:#x}: "
                f"{parts[5:]} != [{mnemonic!r}, {operand!r}]")


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "object-initializer-27550.so"
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-shared", "-fPIC", SOURCE, "-o", library], check=True)
    dll = ctypes.CDLL(str(library))

    run = dll.recovered_object_initializer_27550_run
    run.argtypes = [ctypes.c_void_p] + [ctypes.c_uint] * 8
    run.restype = None

    buf = (ctypes.c_ubyte * OBJECT_SIZE)()
    ctypes.memset(ctypes.byref(buf), SENTINEL, OBJECT_SIZE)
    run(ctypes.byref(buf), CONFIG, CALLBACK, RELATED, KIND, TEAM,
        X, Z, FACING)

    assert u32(buf, 0x6c) == CONFIG, hex(u32(buf, 0x6c))
    assert u32(buf, 0x74) == RELATED, hex(u32(buf, 0x74))
    assert u32(buf, 0x64) == KIND, hex(u32(buf, 0x64))
    assert u32(buf, 0x68) == TEAM, hex(u32(buf, 0x68))
    assert u32(buf, 0x04) == CALLBACK, hex(u32(buf, 0x04))
    assert u16(buf, 0x02) == 1, u16(buf, 0x02)
    assert u16(buf, 0x170) == 1, u16(buf, 0x170)
    assert u32(buf, 0x08) == X, hex(u32(buf, 0x08))
    assert u32(buf, 0x10) == Z, hex(u32(buf, 0x10))
    assert u16(buf, 0x184) == FACING, hex(u16(buf, 0x184))

    for offset in ZERO_HALFWORDS:
        assert u16(buf, offset) == 0, (hex(offset), u16(buf, offset))
    for offset in ZERO_BYTES:
        assert buf[offset] == 0, (hex(offset), buf[offset])

    assert u16(buf, 0x46) == 0xFFFF, hex(u16(buf, 0x46))
    assert u32(buf, 0x1c8) == 0, hex(u32(buf, 0x1c8))
    assert u32(buf, 0x1cc) == 0, hex(u32(buf, 0x1cc))
    for offset in (0x1e2, 0x1e4, 0x1e6, 0x1e8):
        assert u16(buf, offset) == 0x64, (hex(offset), u16(buf, offset))
    for offset in (0x1f8, 0x1fa):
        assert u16(buf, offset) == 0xFFFF, (hex(offset), u16(buf, offset))
    # 0x278ac loads 0xff into g13 before the 0x278b0 halfword store.
    assert u16(buf, 0x1fc) == 0xFF, hex(u16(buf, 0x1fc))

    for offset in UNTOUCHED:
        assert buf[offset] == SENTINEL, (hex(offset), buf[offset])

    table = load_evidence()
    check_evidence(table, BLOCK_EVIDENCE)
    check_evidence(table, TAIL_EVIDENCE)
    for address, _, _ in BLOCK_EVIDENCE:
        if not 0x27550 <= address <= 0x276D4:
            raise AssertionError(f"block evidence outside 0x27550-0x276d4: {address:#x}")

print("PASS: 0x27550 bounded object initializer")
