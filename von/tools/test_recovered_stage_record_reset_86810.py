#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ResetState(ctypes.Structure):
    _fields_ = [("region_5096a0", ctypes.c_uint16 * (0x3b0 // 2)),
                ("region_509a60", ctypes.c_uint16 * 3),
                ("region_509a80", ctypes.c_uint8 * 0x40),
                ("region_509ad0", ctypes.c_uint8 * 0x40),
                ("latch_509ac0", ctypes.c_uint8),
                ("latch_509b10", ctypes.c_uint8),
                ("current_words", ctypes.c_uint32 * 4),
                ("current_pair", ctypes.c_uint32 * 2),
                ("active_words", ctypes.c_uint32 * 4),
                ("active_pair", ctypes.c_uint32 * 2),
                ("previous_words", ctypes.c_uint32 * 4),
                ("previous_pair", ctypes.c_uint32 * 2),
                ("stage_guard", ctypes.c_uint32),
                ("epoch_guard", ctypes.c_uint32),
                ("snapshot_epoch", ctypes.c_uint32),
                ("scalar_509a68", ctypes.c_uint32),
                ("scalar_509a6c", ctypes.c_uint32),
                ("scalar_509a70", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-stage-reset-") as d:
        so = Path(d) / "stage-reset.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_stage_record_reset_86810.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_stage_record_reset_86810
        fn.argtypes = [ctypes.POINTER(ResetState)]
        state = ResetState()
        ctypes.memset(ctypes.byref(state), 0xa5, ctypes.sizeof(state))
        fn(ctypes.byref(state))
        for record in range(0x3b0 // 16):
            base = record * 8
            assert [state.region_5096a0[base + i] for i in
                    (0, 1, 2, 3, 5, 6, 7)] == [0] * 7
            assert state.region_5096a0[base + 4] == 0xa5a5
        assert list(state.region_509a60) == [0, 0, 0]
        assert list(state.region_509a80) == [0] * 0x40
        assert list(state.region_509ad0) == [0] * 0x40
        assert all(value == 0 for value in state.current_words)
        assert all(value == 0 for value in state.active_words)
        assert all(value == 0 for value in state.previous_words)
        assert all(value == 0 for value in state.current_pair)
        assert all(value == 0 for value in state.active_pair)
        assert all(value == 0 for value in state.previous_pair)
        assert (state.stage_guard, state.epoch_guard, state.snapshot_epoch,
                state.scalar_509a68, state.scalar_509a6c,
                state.scalar_509a70) == (0, 0, 0, 0, 0, 0)
        print("PASS: stage record reset tail")


if __name__ == "__main__":
    main()
