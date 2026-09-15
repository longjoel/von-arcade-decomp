#!/usr/bin/env python3
"""Contract for the explicitly non-validation accelerated attract sampler."""
import re
from pathlib import Path

SCRIPT = Path(__file__).with_name("trace_i960_exploratory_accelerated.lua")
RUNNER = Path(__file__).parents[2] / "vonctl/commands/trace.py"


def function_source(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^def {re.escape(name)}\(.*?(?=^def |\Z)", text, re.S | re.M)
    assert match, f"{name} not found in {path}"
    return match.group(0)


def main() -> int:
    text = SCRIPT.read_text(encoding="utf-8")
    for value in ("0x00500090", "0x00500094", "0x005000a4",
                  "0x00057e3f", "0x000be6df", "0x00155cbf", "0x00249eff"):
        assert value in text, value
    assert "exploratory-accelerated-pcs.txt" in text
    assert "exploratory-accelerated-events.log" in text
    assert "exploratory evidence, never authoritative strict evidence" in text
    assert "space:write_u32(HEARTBEAT" in text
    assert "space:write_u32(PHASE" not in text
    assert "space:write_u32(INIT" not in text
    assert "heartbeat_injection" in text
    runner = function_source(RUNNER, "i960_exploratory")
    assert '"vonj"' in runner
    assert "exploratory-accelerated-vonj" in runner
    assert "vonjdev" not in runner
    assert "-bench" in runner
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
