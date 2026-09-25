#!/usr/bin/env python3
"""Replay normalized SHARC packets and compare them with committed matrices.

This verifier deliberately operates on packet words and pushed bases.  It does
not use pivots or a guessed parent tree; lineage is a separate contract gate.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def f16(word: int) -> float:
    value = math.ldexp(1.0 + (word & 0x3FF) / 1024.0,
                       ((word >> 10) & 0x1F) - 15)
    return -value if word & 0x8000 else value


def angle(word: int) -> float:
    signed = word & 0xFFFF
    if signed & 0x8000:
        signed -= 0x10000
    return f32(signed * 0.000095876726845745)


_SIN_COEFFICIENTS = [
    0xAB4F7739, 0x2F3072AB, 0xB2D731A6, 0x3638EF1C,
    0xB9500D01, 0x3C088889, 0xBE2AAAAB,
]


def sharc_sine_poly(residual: float) -> float:
    squared = f32(residual * residual)
    polynomial = struct.unpack("<f", struct.pack("<I", _SIN_COEFFICIENTS[0]))[0]
    for bits in _SIN_COEFFICIENTS[1:]:
        coefficient = struct.unpack("<f", struct.pack("<I", bits))[0]
        polynomial = f32(squared * polynomial + coefficient)
    return f32(f32(squared * polynomial) * residual + residual)


def sharc_sine(value: float) -> float:
    pi = struct.unpack("<f", struct.pack("<I", 0x40491000))[0] + \
        struct.unpack("<f", struct.pack("<I", 0xB715777A))[0]
    quadrant = int(value / pi)
    residual = f32(value - quadrant * pi)
    result = sharc_sine_poly(residual)
    return -result if quadrant & 1 else result


def sharc_cosine(value: float) -> float:
    magnitude = abs(value)
    pi_half = struct.unpack("<f", struct.pack("<I", 0x3FC90FDB))[0]
    phase = f32(pi_half + magnitude)
    reciprocal_pi = struct.unpack("<f", struct.pack("<I", 0x3EA2F983))[0]
    quadrant = int(f32(phase * reciprocal_pi))
    fraction = quadrant - 0.5
    pi_hi = struct.unpack("<f", struct.pack("<I", 0x40491000))[0]
    pi_lo = struct.unpack("<f", struct.pack("<I", 0xB715777A))[0]
    residual = f32(f32(magnitude - f32(pi_hi * fraction)) -
                   f32(pi_lo * fraction))
    result = sharc_sine_poly(residual)
    return -result if quadrant & 1 else result


def replay(base_words: list[int], packet_words: list[int], *, lagged_x: bool = False) -> list[float]:
    matrix = [f32(struct.unpack("<f", struct.pack("<I", word))[0])
              for word in base_words]
    vector = [f16(packet_words[i]) for i in (2, 3, 4)]
    for col in range(3):
        matrix[9 + col] = f32(matrix[9 + col] + sum(
            matrix[row * 3 + col] * vector[row] for row in range(3)))

    # The emitter packet is 22/Z, 21/Y, 20/X.  The service handlers mutate
    # their row pairs in that order (the packet values are already negated by
    # the i960 emitter where applicable).
    for axis, word_index in ((2, 6), (1, 8), (0, 10)):
        if lagged_x and axis == 0:
            # Diagnostic only: the SHARC write trace suggests opcode 0x14 can
            # consume the preceding half-word register value. Do not use this
            # hypothesis for canonical output until it is reproduced across
            # independent captures.
            signed_half = f16(packet_words[8])
            radians = -signed_half * 0.000095876726845745
        else:
            radians = angle(packet_words[word_index])
        sine, cosine = sharc_sine(radians), sharc_cosine(radians)
        first = 3 if axis == 0 else 0
        second = 6 if axis == 0 else (6 if axis == 1 else 3)
        sine = sine if axis == 1 else f32(-sine)
        for col in range(3):
            u, v = matrix[first + col], matrix[second + col]
            matrix[first + col] = f32(cosine * u + sine * v)
            matrix[second + col] = f32(-sine * u + cosine * v)
    return matrix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    document = json.loads(args.fixture.read_text())
    packets = {item["event_id"]: item for item in document["packets"]}
    reports = []
    for program in document["part_programs"]:
        packet = packets.get(program["packet_event_id"])
        if packet is None:
            continue
        actual = replay(program["push"]["base_words"], packet["words"])
        expected = [struct.unpack("<f", struct.pack("<I", word))[0]
                    for word in program["commit"]["matrix_words"]]
        report = {
            "oba": packet["oba"],
            "packet_event_id": packet["event_id"],
            "rotation_error": max(abs(actual[i] - expected[i]) for i in range(9)),
            "translation_error": max(abs(actual[9 + i] - expected[9 + i])
                                      for i in range(3)),
        }
        stack_words = program["commit"].get("stack_words")
        if stack_words:
            stack = [struct.unpack("<f", struct.pack("<I", word))[0]
                     for word in stack_words]
            report["stack_rotation_error"] = max(
                abs(actual[i] - stack[i]) for i in range(9))
            report["stack_translation_error"] = max(
                abs(actual[9 + i] - stack[9 + i]) for i in range(3))
        source_words = program["commit"].get("service_source_words")
        if source_words:
            source = [struct.unpack("<f", struct.pack("<I", word))[0]
                      for word in source_words]
            report["service_rotation_error"] = max(
                abs(actual[i] - source[i]) for i in range(9))
            report["service_translation_error"] = max(
                abs(actual[9 + i] - source[9 + i]) for i in range(3))
        reports.append(report)
        lagged = replay(program["push"]["base_words"], packet["words"],
                        lagged_x=True)
        report["lagged_x_rotation_error"] = max(
            abs(lagged[i] - expected[i]) for i in range(9))
        report["lagged_x_translation_error"] = max(
            abs(lagged[9 + i] - expected[9 + i]) for i in range(3))
    result = {
        "schema_version": 1,
        "parts": reports,
        "max_rotation_error": max((x["rotation_error"] for x in reports), default=0),
        "max_translation_error": max((x["translation_error"] for x in reports), default=0),
        "max_lagged_x_rotation_error": max(
            (x["lagged_x_rotation_error"] for x in reports), default=0),
        "max_lagged_x_translation_error": max(
            (x["lagged_x_translation_error"] for x in reports), default=0),
    }
    stack_reports = [x for x in reports if "stack_rotation_error" in x]
    if stack_reports:
        result["max_stack_rotation_error"] = max(
            x["stack_rotation_error"] for x in stack_reports)
        result["max_stack_translation_error"] = max(
            x["stack_translation_error"] for x in stack_reports)
    source_reports = [x for x in reports if "service_rotation_error" in x]
    if source_reports:
        result["max_service_rotation_error"] = max(
            x["service_rotation_error"] for x in source_reports)
        result["max_service_translation_error"] = max(
            x["service_translation_error"] for x in source_reports)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
