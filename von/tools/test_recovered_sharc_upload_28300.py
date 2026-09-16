#!/usr/bin/env python3
"""Validate the SHARC upload constants and listing evidence for 0x28300."""

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_upload_28300.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

text = SOURCE.read_text(encoding="utf-8")
for fragment in (
        "0x2b1eU", "0x0016b58cU", "0x00980000U", "0x00980020U",
        "0x008c0000U", "0x00884000U", "0x00503ac4U", "0x80000000U",
        "*fifo = 8U"):
    if fragment not in text:
        raise AssertionError(f"upload model missing {fragment}")

listing = LISTING.read_text(encoding="utf-8")
block = listing[listing.index("   28300:"):listing.index("   28410:")]
for evidence in (
        "lda\t0x2b1e,r6", "st\tr6,0x503ac4",
        "st\tg2,0x980000", "st\tg14,0x980020",
        "lda\t0x884000,g7", "st\tg14,0x980000",
        "mov\t8,g2", "st\tg2,0x884000", "ldos\t(r5),g4"):
    if evidence not in block:
        raise AssertionError(f"upload listing evidence missing: {evidence}")

print("PASS: 0x28300 SHARC upload constants and evidence")
