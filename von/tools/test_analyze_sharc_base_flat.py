#!/usr/bin/env python3
"""Regression for the flat pre-multiply body-stream model.

Builds a synthetic push/commit program whose commit is exactly
`R_record * R_base` with `t_base + v`, then requires
`analyze_sharc_base_flat.analyze` to report zero error.
"""

import math
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_sharc_base_flat as model  # noqa: E402


def bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def window(rotation, translation):
    """SHARC 12-word window: [r0..r8, t0,t1,t2]."""
    return [bits(x) for x in list(rotation) + list(translation)]


def main() -> int:
    # base = Rz(25 deg) at (1, 2, 3)
    a = math.radians(25.0)
    base_r = [math.cos(a), -math.sin(a), 0.0,
              math.sin(a), math.cos(a), 0.0,
              0.0, 0.0, 1.0]
    base_t = [1.0, 2.0, 3.0]

    # Record words: [X, Y, Z] angles and fixed-point translation words.
    angle_words = [0x0400, 0x0800, 0x0C00]  # X, Y, Z
    trans_words = [0x3C00, 0x4000, 0x4200]  # fixed16 -> (1, 2, 3)
    v = [model.fixed16(w) for w in trans_words]
    record_r = model.record_rotation(angle_words)
    commit_r = model.matmul(record_r, base_r)
    # Kernel service projects the translation through the base: M^T v.
    commit_t = [base_t[i] + sum(base_r[r * 3 + i] * v[r] for r in range(3))
                for i in range(3)]

    packet_words = [5, 47, trans_words[0], trans_words[1], trans_words[2],
                    22, angle_words[2], 21, angle_words[1], 20, angle_words[0],
                    58, 0, 6]
    fixture = {
        "packets": [{"event_id": 10, "oba": "0x0000000a", "words": packet_words}],
        "part_programs": [{
            "packet_event_id": 10,
            "push": {"depth": 3, "base_words": window(base_r, base_t)},
            "commit": {"depth": 3, "oba": "0x0000000a",
                       "matrix_words": window(commit_r, commit_t)},
        }],
    }
    result = model.analyze(fixture)
    rot_error = max(max(values) for values in result["rot"].values())
    trans_error = max(max(values) for values in result["trans"].values())
    assert rot_error < 1e-3, rot_error
    assert trans_error < 1e-3, trans_error
    print("PASS: flat pre-multiply body model reproduces push/commit exactly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
