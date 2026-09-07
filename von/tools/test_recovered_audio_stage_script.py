#!/usr/bin/env python3
"""Verify the recovered per-stage intro audio scripts against goldens.

Goldens are the exact packet sequences from the full-bout audio-queue tap
(von/build/audio-queue/manual-02/input-audio.log), regenerable with
von/tools/extract_audio_stage_script.py. Structural invariants pin the
interpretation: ascending spawn-relative offsets ending at -1, the shared
core packets in every stage, the per-stage BGM triple AE 13 (0x4a+stage),
and the FIGHT ID byte (0x4f+stage) on the final tick.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_audio_stage_script.c"

GOLDENS: dict[int, list[tuple[int, list[int]]]] = {
    1: [(-121, [0xAE, 0x00, 0x02]), (-111, [0xAE, 0x13, 0x3F]),
        (-73, [0xAE, 0x13, 0x41]), (-64, [0xAE, 0x13, 0x4B]),
        (-54, [0xAE, 0x11, 0x11]), (-33, [0xAE, 0x11, 0x11]),
        (-1, [0xAE, 0x13, 0x50])],
    2: [(-128, [0xAE, 0x11, 0x15]), (-120, [0xAE, 0x11, 0x15]),
        (-120, [0xAE, 0x00, 0x03]), (-120, [0xAE, 0x00, 0x03]),
        (-119, [0xAE, 0x00, 0x02]), (-109, [0xAE, 0x13, 0x3F]),
        (-71, [0xAE, 0x13, 0x41]), (-62, [0xAE, 0x13, 0x4C]),
        (-52, [0xAE, 0x11, 0x11]), (-31, [0xAE, 0x11, 0x11]),
        (-1, [0xAE, 0x13, 0x51])],
    3: [(-128, [0xAE, 0x11, 0x15]), (-121, [0xAE, 0x00, 0x03]),
        (-121, [0xAE, 0x00, 0x03]), (-120, [0xAE, 0x00, 0x02]),
        (-110, [0xAE, 0x13, 0x3F]), (-72, [0xAE, 0x13, 0x41]),
        (-63, [0xAE, 0x13, 0x4D]), (-53, [0xAE, 0x11, 0x11]),
        (-32, [0xAE, 0x11, 0x11]), (-1, [0x52]), (-1, [0xAE, 0x13])],
}

CORE = [[0xAE, 0x00, 0x02], [0xAE, 0x13, 0x3F], [0xAE, 0x13, 0x41],
        [0xAE, 0x11, 0x11]]


class Step(ctypes.Structure):
    _fields_ = [("frame_offset", ctypes.c_int32),
                ("length", ctypes.c_ubyte),
                ("bytes", ctypes.c_ubyte * 3)]


def read_script(recovered, stage: int) -> list[tuple[int, list[int]]]:
    count = recovered.recovered_audio_stage_script_step_count(stage)
    steps = []
    for index in range(count):
        step = Step()
        ok = recovered.recovered_audio_stage_script_step(stage, index,
                                                         ctypes.byref(step))
        assert ok == 1, f"stage {stage} index {index} rejected"
        assert 1 <= step.length <= 3, f"bad length {step.length}"
        steps.append((step.frame_offset,
                      [step.bytes[i] for i in range(step.length)]))
    return steps


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-audio-script-") as directory:
        library = Path(directory) / "audio-script.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_audio_stage_script_step_count.argtypes = [
            ctypes.c_uint32]
        recovered.recovered_audio_stage_script_step_count.restype = (
            ctypes.c_uint32)
        recovered.recovered_audio_stage_script_step.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Step)]
        recovered.recovered_audio_stage_script_step.restype = ctypes.c_uint32

        for stage in (0, 4, 99):
            assert recovered.recovered_audio_stage_script_step_count(
                stage) == 0, f"stage {stage} accepted"
            assert recovered.recovered_audio_stage_script_step(
                stage, 0, ctypes.byref(Step())) == 0, \
                f"stage {stage} step accepted"
        assert recovered.recovered_audio_stage_script_step(
            1, 999, ctypes.byref(Step())) == 0, "overrun accepted"

        checked = 0
        for stage, golden in GOLDENS.items():
            steps = read_script(recovered, stage)
            assert steps == golden, f"stage {stage} mismatch: {steps}"
            offsets = [offset for offset, _ in steps]
            assert offsets == sorted(offsets), "offsets not ascending"
            assert offsets[-1] == -1, "script does not end at spawn -1"
            packets = [bytes_ for _, bytes_ in steps]
            for core in CORE:
                assert core in packets, f"stage {stage} missing {core}"
            assert [0xAE, 0x13, 0x4A + stage] in packets, \
                f"stage {stage} BGM triple missing"
            final = [bytes_ for offset, bytes_ in steps if offset == -1]
            assert any(0x4F + stage in packet for packet in final), \
                f"stage {stage} FIGHT id missing"
            checked += len(steps)
        print(f"PASS: {checked} stage-script steps across 3 stages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
