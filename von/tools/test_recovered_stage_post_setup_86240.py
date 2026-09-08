#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Thresholds(ctypes.Structure):
    _fields_ = [("words", ctypes.c_uint32 * 4),
                ("pair", ctypes.c_uint32 * 2),
                ("b34", ctypes.c_uint32)]


class Snapshot(ctypes.Structure):
    _fields_ = [("active_words", ctypes.c_uint32 * 4),
                ("active_pair", ctypes.c_uint32 * 2),
                ("previous_words", ctypes.c_uint32 * 4),
                ("previous_pair", ctypes.c_uint32 * 2),
                ("stage_guard", ctypes.c_uint32),
                ("epoch_guard", ctypes.c_uint32),
                ("snapshot_epoch", ctypes.c_uint32)]


class ClearState(ctypes.Structure):
    _fields_ = [("region_5096a0", ctypes.c_uint16 * (0x3b0 // 2)),
                ("region_509a60", ctypes.c_uint16 * 3),
                ("region_509a80", ctypes.c_uint8 * 0x40),
                ("region_509ad0", ctypes.c_uint8 * 0x40),
                ("latch_509ac0", ctypes.c_uint8),
                ("latch_509b10", ctypes.c_uint8),
                ("word_509a68", ctypes.c_uint32),
                ("word_509a6c", ctypes.c_uint32),
                ("word_509a70", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-stage-post-setup-") as d:
        so = Path(d) / "stage-post-setup.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_stage_post_setup_86240.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        normalize = lib.recovered_stage_threshold_normalize_86240
        normalize.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                              ctypes.POINTER(Thresholds), ctypes.POINTER(Thresholds)]
        update = lib.recovered_stage_snapshot_update_86240
        update.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.POINTER(Thresholds), ctypes.POINTER(Thresholds),
                           ctypes.POINTER(Snapshot)]
        seed = lib.recovered_stage_mode_seed_86240
        seed.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Thresholds),
                         ctypes.POINTER(Thresholds)]
        seed.restype = ctypes.c_uint32
        clear = lib.recovered_stage_working_tables_clear_86240
        clear.argtypes = [ctypes.POINTER(ClearState)]

        source = Thresholds((0x9c4, 0x5dc, 0x4b0, 0x5dc), (0x7cf, 0x5db), 0)
        out = Thresholds()
        normalize(4, 128, ctypes.byref(source), ctypes.byref(out))
        assert list(out.words) == [0x9c5, 0x5dd, 0x4b1, 0x5dd]
        assert list(out.pair) == [0x7d1, 0x5db]
        assert out.b34 == 0x5dd

        low = Thresholds((0x2bc, 0x1f4, 0x1f4, 0x1f4), (0x1f3, 0x1f3), 0)
        normalize(1, 32, ctypes.byref(low), ctypes.byref(out))
        assert list(out.words) == list(low.words), "low-timing bypass"
        normalize(1, 40, ctypes.byref(low), ctypes.byref(out))
        assert list(out.words) == [0x2bd, 0x1f5, 0x1f5, 0x1f5]
        assert list(out.pair) == [0x1f3, 0x1f3]
        assert out.b34 == 0x1f5

        state = Snapshot()
        effective = Thresholds()
        update(3, 1, 1, ctypes.byref(out), ctypes.byref(effective),
               ctypes.byref(state))
        assert list(state.active_words) == list(out.words)
        assert state.stage_guard == 3
        replacement = Thresholds((1, 2, 3, 4), (5, 6), 7)
        update(4, 1, 2, ctypes.byref(replacement), ctypes.byref(effective),
               ctypes.byref(state))
        assert list(state.previous_words) == [1, 2, 3, 4]
        update(4, 0, 0, ctypes.byref(out), ctypes.byref(effective),
               ctypes.byref(state))
        assert list(effective.words) == [1, 2, 3, 4], "zero-transition restore"
        update(4, 1, 2, ctypes.byref(out), ctypes.byref(effective),
               ctypes.byref(state))
        assert list(effective.words) == list(state.active_words)
        update(4, 1, 2, ctypes.byref(replacement), ctypes.byref(effective),
               ctypes.byref(state))
        assert list(effective.words) == list(state.active_words)
        assert state.snapshot_epoch == 2

        seed_input = Thresholds((9, 9, 9, 9), (9, 9), 0x1234)
        assert seed(0, 0, 1, ctypes.byref(seed_input), ctypes.byref(effective)) == 0
        assert seed(2, 1, 1, ctypes.byref(seed_input), ctypes.byref(effective)) == 0
        assert seed(2, 0, 1, ctypes.byref(seed_input), ctypes.byref(effective)) == 1
        assert list(effective.words) == [0x2bd, 0x1f5, 0x1f5, 0x1f5]
        assert list(effective.pair) == [0x1f5, 0x1f5]
        assert effective.b34 == 0x1234
        assert seed(2, 0, 2, ctypes.byref(seed_input), ctypes.byref(effective)) == 1
        assert list(effective.words) == [0x9c5, 0x5dd, 0x4b1, 0x5dd]
        assert list(effective.pair) == [0x7d1, 0x5dd]
        assert seed(2, 0, 3, ctypes.byref(seed_input), ctypes.byref(effective)) == 1
        assert list(effective.words) == [0xfffffd44] * 4
        assert list(effective.pair) == [0xfffffd44, 0xfffffd44]
        assert seed(2, 0, 255, ctypes.byref(seed_input), ctypes.byref(effective)) == 1
        assert list(effective.words) == [0, 0, 0, 0]

        cleared = ClearState()
        ctypes.memset(ctypes.byref(cleared), 0xa5, ctypes.sizeof(cleared))
        clear(ctypes.byref(cleared))
        for record in range(0x3b0 // 16):
            base = record * 8
            assert [cleared.region_5096a0[base + i] for i in
                    (0, 1, 2, 3, 5, 6, 7)] == [0] * 7
            assert cleared.region_5096a0[base + 4] == 0xa5a5
        assert list(cleared.region_509a60) == [0, 0, 0]
        assert list(cleared.region_509a80) == [0] * 0x40
        assert list(cleared.region_509ad0) == [0] * 0x40
        assert (cleared.latch_509ac0, cleared.latch_509b10,
                cleared.word_509a68, cleared.word_509a6c,
                cleared.word_509a70) == (0, 0, 0, 0, 0)
        print("PASS: stage post-setup threshold and snapshot prefix")


if __name__ == "__main__":
    main()
