#!/usr/bin/env python3
"""Self-contained emulation of the SHARC geometry-transform opcodes.

The Model 2 geometry DSP (SHARC) turns a 6-word per-part animation record into
a 3x4 transform by running the recovered packet program. This module
reimplements the recovered opcode models (von/i960/recovered_sharc_opcode_*.c)
so the animation can be built from ROM records without MAME.

Packet program (recovered_geometry_object_packet.c):
    0x2f, base[3], 0x16, p16, 0x15, p15, 0x14, p14, 0x3a (commit)
Opcode semantics (each recovered and golden-tested against MAME):
    0x14  R = Rx * R          (X row-pair rotation)
    0x15  R = Ry * R          (Y row-pair rotation)
    0x16  R = Rz * R          (Z row-pair rotation)
    0x30/0x2f  tail = v^T * R (translation), then a scaled-Z rebuild
    0x3a  commit 12 matrix words + tail

The angle unit is `word * pi/32767` (recovered opcode-0x30 model).
"""
from __future__ import annotations

import math
import struct


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def s16(word: int) -> int:
    word &= 0xFFFF
    return word - 0x10000 if word >= 0x8000 else word


def angle_radians(word: int) -> float:
    return s16(word) * math.pi / 32767.0


def _sincos(word: int) -> tuple[float, float]:
    angle = angle_radians(word)
    return f32(math.sin(angle)), f32(math.cos(angle))


def rotate_x(matrix: list[float], sine: float, cosine: float) -> list[float]:
    """Recovered opcode 0x14: rows 1/2 (Y,Z) rotate about X."""
    s, c = f32(sine), f32(cosine)
    row1 = [f32(f32(c * matrix[3 + col]) - f32(s * matrix[6 + col])) for col in range(3)]
    row2 = [f32(f32(s * matrix[3 + col]) + f32(c * matrix[6 + col])) for col in range(3)]
    return list(matrix[:3]) + row1 + row2


def rotate_y(matrix: list[float], sine: float, cosine: float) -> list[float]:
    """Recovered opcode 0x15: rows 0/2 (X,Z) rotate about Y."""
    s, c = f32(sine), f32(cosine)
    out = [0.0] * 3 + list(matrix[3:6]) + [0.0] * 3
    for row in range(3):
        x, z = matrix[row], matrix[6 + row]
        out[row] = f32(f32(c * x) + f32(s * z))
        out[6 + row] = f32(f32(-s * x) + f32(c * z))
    return out


def rotate_z(matrix: list[float], sine: float, cosine: float) -> list[float]:
    """Recovered opcode 0x16: rows 0/1 (X,Y) rotate about Z."""
    s, c = f32(sine), f32(cosine)
    out = [0.0] * 6 + list(matrix[6:9])
    for col in range(3):
        x, y = matrix[col], matrix[3 + col]
        out[col] = f32(f32(c * x) - f32(s * y))
        out[3 + col] = f32(f32(s * x) + f32(c * y))
    return out


def translation_tail(translation: list[float], matrix: list[float]) -> list[float]:
    """Recovered opcode 0x2f/0x30: tail = v^T * R (column dot v)."""
    tail = []
    for col in range(3):
        acc = 0.0
        for row in range(3):
            acc = f32(acc + f32(translation[row] * matrix[row * 3 + col]))
        tail.append(acc)
    return tail


def compose_record(record: list[int], prior: list[float] | None = None
                   ) -> tuple[list[float], list[float]]:
    """Run one 6-word record through the recovered packet program.

    Record layout (from the 0x8d400 emitter): (y_angle, z_angle,
    translation[3], x_angle) as signed 16-bit words. `prior` is the parent's
    cumulative 3x3 rotation (identity for a root part). Returns (matrix, tail).
    """
    y_angle, z_angle, tx, ty, tz, x_angle = [s16(w) for w in record]
    base = list(prior) if prior is not None else [1.0, 0.0, 0.0,
                                                  0.0, 1.0, 0.0,
                                                  0.0, 0.0, 1.0]
    tail = translation_tail([f32(tx), f32(ty), f32(tz)], base)
    z_sin, z_cos = _sincos(z_angle)
    y_sin, y_cos = _sincos(y_angle)
    x_sin, x_cos = _sincos(x_angle)
    matrix = rotate_x(rotate_y(rotate_z(base, z_sin, z_cos), y_sin, y_cos),
                      x_sin, x_cos)
    return matrix, tail


def main() -> int:
    # Opcode-0x30 golden: translation (2,3,4) against prior rows 1..9 ->
    # tail = (42,51,60); zero angles leave the prior rotation untouched.
    prior = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    matrix, tail = compose_record([0, 0, 2, 3, 4, 0], prior)
    assert tail == [42.0, 51.0, 60.0], tail
    assert matrix == prior, matrix

    # Identity base + zero angles is identity.
    matrix, tail = compose_record([0, 0, 0, 0, 0, 0])
    assert tail == [0.0, 0.0, 0.0], tail
    assert matrix == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0], matrix

    # A quarter turn rotates a unit axis (magnitude preserved).
    matrix, _ = compose_record([0x4000, 0, 0, 0, 0, 0])
    assert abs(math.hypot(matrix[2], matrix[8]) - 1.0) < 1e-3, matrix
    print("PASS: self-contained SHARC transform emulation (opcodes 0x14/0x15/0x16/0x2f)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
