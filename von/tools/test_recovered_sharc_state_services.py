#!/usr/bin/env python3
"""Verify the SHARC 08/0e/10/11/19 state-service models.

Goldens mirror the live harness evidence, not the emulator:
- 0e stores mirror von/tools/sharc_harness_goldens.json effects_exact
  for words 11111111/22222222/33333333/44444444 at DM 0x30105-08.
- 10 init mirrors the golden over deadbeef garbage pokes at 0x30200.
- 11 readback mirrors the live identity stream (12 words; the word
  after the twelve drains empty-FIFO zero, observed 0x0 after
  identity init).
- 19 counter mirrors the live poke proof (counter poked to 5 drains
  back 00000005) and the 08-init zero point.
- The push composition ties the committed
  sharc_stack_push_depth gate (depth 0 -> 1 -> 2 -> 3) to the counter
  emitter; the live 0-to-3 drain is harness-annotated as manually
  proven, since the attract-mode 08 stream resets the counter between
  spaced FIFO probes.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATE_SOURCE = ROOT / "von/i960/recovered_sharc_state_08_0e_10_11_19.c"
STACK_SOURCE = ROOT / "von/i960/recovered_sharc_stack_05_06.c"

IDENTITY = [0x3F800000 if i in (0, 4, 8) else 0 for i in range(12)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-state-") as directory:
        library = Path(directory) / "state.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c99", "-O2", "-shared",
             "-fPIC", str(STATE_SOURCE), str(STACK_SOURCE),
             "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))

        init08 = lib.sharc_service_init_08
        init08.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        init08.restype = None
        dm = (ctypes.c_uint32 * 2)(0xDEAD, 0xBEEF)
        init08(dm)
        assert (dm[0], dm[1]) == (0, 0x30200), (hex(dm[0]), hex(dm[1]))

        upload = lib.sharc_state_upload_0e
        upload.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                           ctypes.POINTER(ctypes.c_uint32)]
        upload.restype = None
        mem = (ctypes.c_uint32 * 4)(0, 0, 0, 0)
        words = (ctypes.c_uint32 * 4)(0x11111111, 0x22222222,
                                      0x33333333, 0x44444444)
        upload(mem, words)
        assert list(mem) == [0x11111111, 0x22222222,
                             0x33333333, 0x44444444]

        init10 = lib.sharc_state_init_10
        init10.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        init10.restype = None
        rec = (ctypes.c_uint32 * 12)(*[0xDEADBEEF] * 12)
        init10(rec)
        assert list(rec) == IDENTITY, [hex(v) for v in rec]

        readback = lib.sharc_state_readback_11
        readback.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                             ctypes.POINTER(ctypes.c_uint32)]
        readback.restype = None
        # Twelve words only: the listing shows 12 reads and 12 emits
        # (twelfth emit in the RTS delay slot); a thirteenth drained
        # word is empty-FIFO zero, proven live.
        src = (ctypes.c_uint32 * 12)(*IDENTITY)
        out = (ctypes.c_uint32 * 12)()
        readback(src, out)
        assert list(out) == IDENTITY
        pattern = (ctypes.c_uint32 * 12)(*range(1, 13))
        readback(pattern, out)
        assert list(out) == list(range(1, 13))

        counter = lib.sharc_state_counter_19
        counter.argtypes = [ctypes.c_uint32]
        counter.restype = ctypes.c_uint32
        for depth in (0, 3, 5, 7):
            assert counter(depth) == depth

        push = lib.sharc_stack_push_depth
        push.argtypes = [ctypes.c_uint32]
        push.restype = ctypes.c_uint32
        depth = 0
        for _ in range(3):
            depth = push(depth)
        assert depth == 3
        assert counter(depth) == 3

        print("PASS: SHARC 08/0e/10/11/19 state services "
              "(harness/live goldens + push composition)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
