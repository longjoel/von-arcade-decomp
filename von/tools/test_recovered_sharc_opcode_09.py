#!/usr/bin/env python3
"""Validate the four-vector transform recovered for SHARC opcode 0x09.

Grouping contract (live-proven): the handler dots four CONSECUTIVE FIFO
triplets (words 3k..3k+2 form vector k) with the record matrix columns.
An earlier revision regrouped lane-major (x0,y0,z0)..; the 07->09->1a->11
matrix compose refutes that: a cyclic-shift matrix maps each input triplet
to its shifted self in place, which a lane regroup would have scattered.
The identified main-CPU caller still packs three lane quadwords, so how
those lanes map to geometric vectors stays open (see the 09 ledger unit);
only the SHARC-side grouping below is pinned.
"""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_09.c"

# Live matrix-compose vectors (forced-FIFO 07/09/1a/11 spec, both engines
# agree on the 09 stage: 0/1 scalings are exact).
LIVE_V = (0x3DCCCCCD, 0x3FD9999A, 0x3F000000, 0x42C80000,
          0x3E4CCCCD, 0x40000000, 0x3EAAAAAB, 0x43480000,
          0x3E99999A, 0x40400000, 0x40E00000, 0x43960000)
# Cyclic-shift matrix out=(y,z,x): [0,0,1, 1,0,0, 0,1,0].
LIVE_SHIFT = (0x00000000, 0x00000000, 0x3F800000,
              0x3F800000, 0x00000000, 0x00000000,
              0x00000000, 0x3F800000, 0x00000000)
# Live 11 readback of the derived record (both boots, both engines).
LIVE_DERIVED = (0x3FD9999A, 0x3F000000, 0x3DCCCCCD,
                0x3E4CCCCD, 0x40000000, 0x42C80000,
                0x43480000, 0x3E99999A, 0x3EAAAAAB,
                0x40E00000, 0x43960000, 0x40400000)


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode09.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        transform = lib.recovered_sharc_opcode_09_transform
        transform.argtypes = [ctypes.POINTER(ctypes.c_float)] * 3
        transform.restype = None
        state_vector = lib.recovered_sharc_opcode_09_state_vector
        state_vector.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_uint,
                                 ctypes.POINTER(ctypes.c_float)]
        state_vector.restype = None

        # Consecutive-triplet grouping: words 3k..3k+2 form vector k.
        stream = (ctypes.c_float * 12)(*[float(i) for i in range(1, 13)])
        coordinates = (ctypes.c_float * 3)()
        for vector, expected in enumerate(((1, 2, 3), (4, 5, 6),
                                           (7, 8, 9), (10, 11, 12))):
            state_vector(stream, vector, coordinates)
            assert tuple(coordinates) == expected

        identity = (ctypes.c_float * 9)(1, 0, 0, 0, 1, 0, 0, 0, 1)
        output = (ctypes.c_float * 12)()
        transform(stream, identity, output)
        assert tuple(output) == tuple(float(i) for i in range(1, 13))

        # General column-dot over consecutive triplets.
        matrix = (ctypes.c_float * 9)(1, 2, 3, 4, 5, 6, 7, 8, 9)
        transform(stream, matrix, output)
        expected = []
        for vector in range(4):
            x, y, z = float(3 * vector + 1), float(3 * vector + 2), float(3 * vector + 3)
            expected.extend((x + 4*y + 7*z, 2*x + 5*y + 8*z, 3*x + 6*y + 9*z))
        for actual, wanted in zip(output, expected):
            assert math.isclose(actual, wanted, rel_tol=0.0, abs_tol=1e-4)

        # Live cyclic-shift compose: bit-exact float words both engines.
        import struct
        live_in = (ctypes.c_float * 12)(
            *[struct.unpack('<f', struct.pack('<I', w))[0] for w in LIVE_V])
        live_mat = (ctypes.c_float * 9)(
            *[struct.unpack('<f', struct.pack('<I', w))[0] for w in LIVE_SHIFT])
        transform(live_in, live_mat, output)
        got = [struct.unpack('<I', struct.pack('<f', v))[0] for v in output]
        assert tuple(got) == LIVE_DERIVED, [hex(v) for v in got]
    print("PASS: SHARC opcode-0x09 four-vector matrix transform")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
