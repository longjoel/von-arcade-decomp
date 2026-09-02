#!/usr/bin/env python3
"""Guard the direct host-FIFO probe used for interpreter/DRC parity checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "von/tools/probe_sharc_opcode_0f_poll.lua"


def main() -> int:
    source = PROBE.read_text(encoding="utf-8")
    required = (
        "0x00000008",
        "0x0000000f",
        "0x3f800000",
        "0xbf800000",
        "space:read_u32(0x00884000)",
        "response-poll=",
        "manager.machine:exit()",
    )
    for fragment in required:
        if fragment not in source:
            raise SystemExit(f"opcode-0x0f DRC poll probe missing {fragment}")
    if source.count("{ 0x") != 7:
        raise SystemExit("opcode-0x0f DRC poll probe does not contain seven vectors")
    verifier = (ROOT / "von/tools/verify_sharc_opcode_0f_poll.py").read_text(encoding="utf-8")
    if "0x00001FFF" not in verifier or "0xFFFFE000" not in verifier:
        raise SystemExit("opcode-0x0f poll verifier is missing signed results")
    nonfinite = (ROOT / "von/tools/probe_sharc_opcode_0f_nonfinite_poll.lua").read_text(encoding="utf-8")
    if (nonfinite.count("{ 0x") != 8 or
            "space:read_u32(0x00884000)" not in nonfinite or
            'state_value("ASTAT")' not in nonfinite or
            'state_value("STKY")' not in nonfinite):
        raise SystemExit("opcode-0x0f nonfinite poll probe is incomplete")
    nonfinite_verifier = (ROOT / "von/tools/verify_sharc_opcode_0f_nonfinite_poll.py").read_text(encoding="utf-8")
    if "--engine" not in nonfinite_verifier or "DRC_EXPECTED" not in nonfinite_verifier:
        raise SystemExit("opcode-0x0f nonfinite verifier lacks engine-specific expectations")
    state_verifier = (ROOT / "von/tools/verify_sharc_opcode_0f_state.py").read_text(encoding="utf-8")
    if "STKY.AIS" not in state_verifier or "--engine" not in state_verifier:
        raise SystemExit("opcode-0x0f state verifier lacks sticky-AIS coverage")
    print("PASS: SHARC opcode-0x0f finite/nonfinite direct FIFO probe contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
