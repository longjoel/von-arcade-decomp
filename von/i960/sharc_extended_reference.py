"""Small exact reference model for the ADSP-2106x floating-point boundary.

This is deliberately independent of MAME's host-float implementation.  It
models the normal/zero subset needed by the precision fixtures and is intended
as an oracle for a future interpreter/DRC implementation.
"""

from fractions import Fraction


WIDTH = 40
FRACTION_BITS = 31
EXPONENT_BIAS = 127
FRACTION_MASK = (1 << FRACTION_BITS) - 1


def decode(value: int) -> Fraction:
    sign = -1 if value & (1 << 39) else 1
    exponent = (value >> FRACTION_BITS) & 0xff
    fraction = value & FRACTION_MASK
    if exponent == 0:
        assert fraction == 0, "denormal reference inputs are outside this model"
        return Fraction(0)
    assert exponent != 0xff, "non-finite reference inputs are outside this model"
    significand = (1 << FRACTION_BITS) | fraction
    shift = exponent - EXPONENT_BIAS - FRACTION_BITS
    scale = 2**shift if shift >= 0 else Fraction(1, 2**-shift)
    return sign * significand * scale


def _floor_log2(value: Fraction) -> int:
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    if value < Fraction(2**exponent):
        exponent -= 1
    elif value >= Fraction(2 ** (exponent + 1)):
        exponent += 1
    return exponent


def encode(value: Fraction, precision: int = 32, truncate: bool = True) -> int:
    if not value:
        return 0
    sign = 1 if value < 0 else 0
    magnitude = -value if value < 0 else value
    exponent = _floor_log2(magnitude)
    shift = exponent - (precision - 1)
    scaled = magnitude * (2**-shift if shift < 0 else Fraction(1, 2**shift))
    quotient, remainder = divmod(scaled.numerator, scaled.denominator)
    if not truncate and (2 * remainder > scaled.denominator or
                         (2 * remainder == scaled.denominator and quotient & 1)):
        quotient += 1
    if quotient == (1 << precision):
        quotient >>= 1
        exponent += 1
    assert quotient == (1 << (precision - 1)) or quotient > (1 << (precision - 1))
    assert quotient < (1 << precision)
    exponent_field = exponent + EXPONENT_BIAS
    assert 1 <= exponent_field <= 254
    fraction = quotient - (1 << (precision - 1))
    if precision < 32:
        fraction <<= 32 - precision
    return (sign << 39) | (exponent_field << FRACTION_BITS) | fraction


def prepare(value: int, rnd32: bool, truncate: bool = True) -> int:
    return encode(decode(value), 24 if rnd32 else 32, truncate)


def binary(operation: str, x: int, y: int, rnd32: bool, truncate: bool = True) -> int:
    x = prepare(x, rnd32, truncate)
    y = prepare(y, rnd32, truncate)
    left, right = decode(x), decode(y)
    result = left + right if operation == "FADD" else left * right
    return encode(result, 24 if rnd32 else 32, truncate)


def float_integer(value: int) -> int:
    return encode(Fraction(value), 32, True)
