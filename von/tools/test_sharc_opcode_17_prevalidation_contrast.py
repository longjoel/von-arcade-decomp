#!/usr/bin/env python3
"""Audit the reproducible opcode-0x17 prevalidation contrast probe."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "von/tools/probe_sharc_opcode_17_prevalidation_contrast.lua"
VERIFY = ROOT / "von/tools/verify_sharc_opcode_17_prevalidation_contrast.py"


probe = PROBE.read_text(encoding="utf-8")
verify = VERIFY.read_text(encoding="utf-8")

required_probe = (
    "local record = {",
    "0x3f800000, 0x40000000, 0x40a00000,",
    "data_space:write_u32(0x00030200, 2)",
    "data_space:write_u32(0x00030201, 0)",
    "data_space:write_u32(0x00030202, 1)",
    "for index, value in ipairs(record2) do",
    "command(0x0d, 0x00000000)",
    "pending = frame + 20",
    "command(0x17)",
    "word(0x00000000)",
    "if frame >= 1100 then",
)
for fragment in required_probe:
    if fragment not in probe:
        raise SystemExit(f"contrast probe missing {fragment!r}")

required_verifier = (
    'pc=020e4d ',
    'pc=020e50 ',
    '00000002", "bcdd67c8", "00000000',
    "normal contrast probe marker missing",
)
for fragment in required_verifier:
    if fragment not in verify:
        raise SystemExit(f"contrast verifier missing {fragment!r}")

print("PASS: opcode-0x17 prevalidation contrast probe contract")
