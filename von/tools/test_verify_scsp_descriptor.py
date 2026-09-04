#!/usr/bin/env python3
"""Contract tests for exact SCSP descriptor verification."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import wave
from pathlib import Path

from verify_scsp_descriptor import pcm8_to_pcm16, swap_words, validate


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        rom_a, rom_b = root / "a.bin", root / "b.bin"
        rom_a.write_bytes(bytes((0x01, 0x80, 0x7f, 0xff)))
        rom_b.write_bytes(bytes((0x10, 0x20, 0x30, 0x40)))
        sample = swap_words(rom_a.read_bytes() + rom_b.read_bytes())
        raw = sample[:4]
        pcm = pcm8_to_pcm16(raw)
        with wave.open(str(root / "sample.wav"), "wb") as output:
            output.setnchannels(1); output.setsampwidth(2); output.setframerate(88200); output.writeframes(pcm)
        catalog = {"format": "runtime-scsp", "rate": 88200, "entries": [{
            "status": "extracted", "wav": "sample.wav", "slot": 2,
            "sa": 0, "lsa": 0, "lea": 4, "pcm8": 1,
        }]}
        result = validate(catalog, sample, root)
        assert result[0]["claims"]["audio_descriptor"] == "validated"
        assert result[0]["pcm_sha256"] == hashlib.sha256(pcm).hexdigest()
        broken = copy.deepcopy(catalog)
        broken["entries"][0]["lea"] = 6
        try:
            validate(broken, sample, root)
        except ValueError as error:
            assert "frame count" in str(error) or "PCM does not match" in str(error) or "exceeds" in str(error)
        else:
            raise AssertionError("mismatched descriptor was accepted")
        broken = copy.deepcopy(catalog)
        broken["entries"][0]["lsa"] = 5
        try:
            validate(broken, sample, root)
        except ValueError as error:
            assert "LSA" in str(error)
        else:
            raise AssertionError("invalid loop address was accepted")
    print("PASS: SCSP descriptor verification binds exact PCM and WAV metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
