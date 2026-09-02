#!/usr/bin/env python3
"""Audit the trigonometric constants used by the SHARC fixed-point helpers."""

from __future__ import annotations

import math
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def float32(word: int) -> float:
    return struct.unpack(">f", word.to_bytes(4, "big"))[0]


def load_listing() -> dict[str, str]:
    result: dict[str, str] = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            slot, body = line.split(":", 1)
            if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
                result[slot] = body
    return result


def main() -> int:
    lines = load_listing()
    expected_words = [
        0x3EA2F983, 0x40491000, 0xB715777A, 0x35800000,
        0xAB4F7739, 0x2F3072AB, 0xB2D731A6, 0x3638EF1C,
        0xB9500D01, 0x3C088889, 0xBE2AAAAB,
    ]
    actual_words = []
    for slot in ("0f5", "0f6", "0f7", "0f8", "0f9", "0fa", "0fb", "0fc", "0fd", "0fe", "0ff"):
        body = lines.get(slot, "")
        marker = "DM(I0, M0) = 0x"
        if marker not in body:
            raise SystemExit(f"SHARC trigonometric table slot {slot} missing constant")
        actual_words.append(int(body.split(marker, 1)[1].split()[0], 16))
    if actual_words != expected_words:
        raise SystemExit(f"unexpected DM 0x3030c constants: {actual_words!r}")

    coefficients = [float32(word) for word in expected_words]
    if not math.isclose(coefficients[0], 1.0 / math.pi, rel_tol=0, abs_tol=2e-7):
        raise SystemExit("DM 0x3030c[0] is not the reciprocal-pi reducer")
    if not math.isclose(coefficients[1], math.pi, rel_tol=0, abs_tol=2e-5):
        raise SystemExit("DM 0x3030c[1] is not the pi reducer")

    # The final seven entries are the odd sine-series coefficients x^15..x^3,
    # stored in descending order for the Horner loop.
    for power, coefficient in zip(range(15, 2, -2), coefficients[-7:]):
        expected = (-1.0 if ((power - 1) // 2) % 2 else 1.0) / math.factorial(power)
        if not math.isclose(coefficient, expected, rel_tol=0, abs_tol=5e-9):
            raise SystemExit(f"unexpected sine coefficient for x^{power}: {coefficient}")

    scale = float32(0x38C9116D)
    if not math.isclose(scale, math.pi / 32767.0, rel_tol=0, abs_tol=2e-12):
        raise SystemExit("0x38c9116d is not the signed-16 angle scale")
    print("PASS: SHARC fixed-point helpers use pi/32767 scaling and sine-series constants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
