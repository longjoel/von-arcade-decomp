#!/usr/bin/env python3
"""Validate the architecture-level SHARC precision fixture schema."""

import json
import pathlib
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "i960"))
from sharc_extended_reference import binary, decode, float_integer  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "i960/sharc_precision_fixtures.json"


def raw(value):
    if not isinstance(value, str) or not value.startswith("0x"):
        raise AssertionError(f"raw value is not hexadecimal: {value!r}")
    parsed = int(value, 16)
    if not 0 <= parsed < (1 << 40):
        raise AssertionError(f"raw value exceeds 40 bits: {value}")
    return parsed


def main():
    document = json.loads(FIXTURE.read_text())
    fmt = document["format"]
    assert fmt["width_bits"] == 40
    assert fmt["sign_bit"] == 39
    assert fmt["exponent_bits"] == [38, 31]
    assert fmt["fraction_bits"] == [30, 0]

    vectors = document["vectors"]
    names = {vector["name"] for vector in vectors}
    required = {
        "fadd_preserves_extended_lsb",
        "fadd_rnd32_clears_input_and_output_lsb",
        "fmul_preserves_extended_lsb",
        "fmul_rnd32_clears_input_and_output_lsb",
        "fadd_nearest_even_tie_down",
        "fadd_nearest_even_tie_up",
        "fadd_truncate_tie",
        "fmul_wide_significand_does_not_wrap",
        "fmul_wide_significand_rnd32_does_not_wrap",
        "fadd_far_exponent_does_not_overflow_alignment",
        "fadd_negative_preserves_extended_lsb",
        "fmul_negative_preserves_extended_lsb",
        "float_3_is_always_extended_boundary",
    }
    assert names == required

    for vector in vectors:
        expected = raw(vector["expected"])
        mode = vector["mode1"]
        if vector["operation"] == "FLOAT":
            assert vector["integer"] == 3
            assert expected == float_integer(vector["integer"])
            continue

        x = raw(vector["x"])
        y = raw(vector["y"])
        assert x in (
            0x0000000000, 0x8000000000, 0x3F80000000, 0x3F80000001,
            0x3FFFFFFFFF,
        )
        assert y in (
            0x2F00000000, 0x2F80000000, 0x3F80000000, 0x3F80000001,
            0x3FFFFFFFFF, 0xBF80000000, 0xBF80000001,
        )
        assert binary(vector["operation"], x, y, mode["rnd32"], mode["trunc"]) == expected

    print("PASS: SHARC 40-bit precision fixture contract")


if __name__ == "__main__":
    main()
