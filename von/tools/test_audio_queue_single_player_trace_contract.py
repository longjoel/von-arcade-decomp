#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def function_source(path: Path, name: str) -> str:
    text = path.read_text()
    match = re.search(rf"^def {re.escape(name)}\(.*?(?=^def |\Z)", text, re.S | re.M)
    assert match, f"{name} not found in {path}"
    return match.group(0)


lua = (ROOT / "von/tools/capture_single_player.lua").read_text()
runner = function_source(ROOT / "vonctl/commands/trace.py", "i960_audio_queue_single_player")
capture_runner = function_source(ROOT / "vonctl/commands/capture.py", "single_player")

assert 'os.getenv("VON_CAPTURE_QUEUE_TRACE") == "1"' in lua
assert "VON_CAPTURE_QUEUE_MAX_SAMPLES" in lua
assert "0x0051aa70" in lua and "0x0051aa74" in lua and "0x0051aa80" in lua
assert "0x0002a4e0" in lua and "0x0002a574" in lua
assert "source=original-vonj" in lua
assert '"VON_CAPTURE_SELECTOR_COUNT": "1"' in runner
assert '"VON_CAPTURE_SELECTOR_START": steps' in runner
assert "VON_CAPTURE_SELECTOR_STEPS" in runner
assert '"VON_CAPTURE_ENABLE_PC_TRACE": "0"' in runner
assert '"VON_CAPTURE_QUEUE_TRACE": "1"' in runner
assert 'config.env("VON_CAPTURE_QUEUE_TRACE", "0")' in capture_runner
assert "vonjdev" not in lua and "vonjdev" not in runner
assert "clean-plain-rompath" not in runner
print("PASS: original-vonj single-player queue trace contract")
