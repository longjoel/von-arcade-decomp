/* Recovered contract for SHARC opcode 0x1d at 0x203ce. */
#include <stdint.h>
#include <math.h>

static float bits_float(uint32_t bits)
{
    union { uint32_t bits; float value; } converted = { bits };
    return converted.value;
}

static uint32_t float_bits(float value)
{
    union { float value; uint32_t bits; } converted = { value };
    return converted.bits;
}

static float rounded_mul(float left, float right)
{
    volatile float result = left * right;
    return result;
}

extern uint32_t recovered_sharc_helper_20dc4_sine(uint32_t magnitude, int negative);

/*
 * The first FIFO word is a signed 16-bit angle.  The delayed second read is
 * R15, and the final F0 = F0 * F15 uses its raw register-file alias as a
 * single-precision multiplier; it is not sign-extended as a second angle.
 */
uint32_t recovered_sharc_opcode_1d(uint32_t angle_word, uint32_t multiplier_bits)
{
    int16_t signed_angle = (int16_t)(angle_word & 0xffffU);
    int negative = signed_angle < 0;
    int magnitude_word = negative ? -(int)signed_angle : (int)signed_angle;
    float radians = rounded_mul((float)magnitude_word, bits_float(0x38c9116d));
    uint32_t sine_bits = recovered_sharc_helper_20dc4_sine(float_bits(radians), negative);
    return float_bits(rounded_mul(bits_float(sine_bits), bits_float(multiplier_bits)));
}
