#!/usr/bin/env python3
"""Guard the controlled opcode-0x17 nonzero probe contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "von/tools/probe_sharc_opcode_17_nonzero.lua"


def main() -> int:
    text = PROBE.read_text(encoding="utf-8")
    required = (
        'manager.machine.devices[":copro_adsp"]',
        'data_space:write_u32(0x00030103, 0x00030200)',
        'data_space:write_u32(0x00030200, 1)',
        'data_space:write_u32(0x00030201, 0)',
        'data_space:write_u32(0x00030104, 0x00030300)',
        'data_space:write_u32(0x000302ff + index, value)',
        'fifo_space:write_u32(0x00884000, 0x00000017)',
        'fifo_space:write_u32(0x00884000, 0x00000000)',
        'log("probe: command=0x17 operands=0,0,0")',
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"opcode-0x17 nonzero probe missing {fragment}")
    print("PASS: SHARC opcode-0x17 nonzero probe table/framing contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
