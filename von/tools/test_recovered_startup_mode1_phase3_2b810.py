#!/usr/bin/env python3
"""Vectors for the mode-1 phase-3 arm at i960 0x2b810.

The attract vector (phase 3, helper g4/g1/g14 = 0) comes from the ordered
input-free fixture in von/build/disasm/mode-transitions.log and the register
probe that observed 0x503a04 = 0xffffffff -> 0, 0x503a00 3 -> 4, and the
0x100a004/0x504d28/0x504d30 attribute words 0x200/0x200/0x4000.
"""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("phase", ctypes.c_uint32),
        ("video_attr", ctypes.c_uint32),
        ("text_attr", ctypes.c_uint32),
        ("text_attr2", ctypes.c_uint32),
        ("progress", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        so = pathlib.Path(tmp) / "phase3.so"
        subprocess.run([
            "cc", "-shared", "-fPIC", "-O2", "-o", str(so),
            str(ROOT / "von/i960/recovered_startup_mode1_phase3_2b810.c"),
        ], check=True)
        fn = ctypes.CDLL(str(so)).recovered_startup_mode1_phase3_run_2b810
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_uint32, ctypes.POINTER(Result)]

        def run(phase, g4, g1, g14):
            out = Result()
            fn(phase, g4, g1, g14, ctypes.byref(out))
            return out

        # Observed input-free attract arm: phase 3 -> 4, attributes 0x200/0x200/
        # 0x4000, progress cleared from 0xffffffff to 0.
        attract = run(3, 0, 0, 0)
        assert attract.phase == 4, hex(attract.phase)
        assert attract.video_attr == 0x200, hex(attract.video_attr)
        assert attract.text_attr == 0x200, hex(attract.text_attr)
        assert attract.text_attr2 == 0x4000, hex(attract.text_attr2)
        assert attract.progress == 0, hex(attract.progress)

        # Helper result bits are ORed in, not replaced.
        general = run(0, 0x1, 0x8000, 0xdeadbeef)
        assert general.phase == 1
        assert general.video_attr == 0x201
        assert general.text_attr == 0x201
        assert general.text_attr2 == 0xC000
        assert general.progress == 0xdeadbeef

        # Phase wraps like the original 32-bit store.
        wrapped = run(0xffffffff, 0, 0, 7)
        assert wrapped.phase == 0
        assert wrapped.progress == 7

    print("PASS: original 0x2b810 mode-1 phase-3 arm vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
