#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def function_source(path: Path, name: str) -> str:
    text = path.read_text()
    match = re.search(rf"^def {re.escape(name)}\(.*?(?=^def |\Z)", text, re.S | re.M)
    assert match, f"{name} not found in {path}"
    return match.group(0)


lua = (ROOT / "von/tools/trace_i960_audio_queue_original.lua").read_text()
runner = function_source(ROOT / "vonctl/commands/trace.py", "i960_audio_queue")

assert "source=original-vonj" in lua
assert "vonjdev" in lua
assert "VON_AUDIO_QUEUE_MAX_SAMPLES" in lua
assert "samples < max_samples" in lua
assert 'io.open(output_path, "a")' in lua
assert "track_pc_visited" in lua
assert "0x0051aa70" in lua and "0x0051aa74" in lua and "0x0051aa80" in lua
assert '"vonj"' in runner
assert "vonjdev" not in runner
assert "clean-plain-rompath" not in runner
assert "-bench" in runner and "-autoboot_script" in runner
print("PASS: original-vonj audio queue trace contract")
