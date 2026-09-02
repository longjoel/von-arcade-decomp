/* Recovered contract for SHARC opcode 0x1e at 0x203dc. */
#include <stdint.h>

typedef unsigned int u32;

static float bits_float(u32 bits)
{
    union { u32 bits; float value; } converted = { bits };
    return converted.value;
}

static u32 float_bits(float value)
{
    union { float value; u32 bits; } converted = { value };
    return converted.bits;
}

static float rounded_mul(float left, float right)
{
    volatile float result = left * right;
    return result;
}

extern u32 recovered_sharc_helper_20dbe_cosine(u32 magnitude, int negative);

/* The first word is a signed half-turn angle; the delayed R15 word is F15. */
u32 recovered_sharc_opcode_1e(u32 angle_word, u32 multiplier_bits)
{
    int16_t signed_angle = (int16_t)(angle_word & 0xffffU);
    int negative = signed_angle < 0;
    int magnitude_word = negative ? -(int)signed_angle : (int)signed_angle;
    float radians = rounded_mul((float)magnitude_word, bits_float(0x38c9116d));
    u32 cosine_bits = recovered_sharc_helper_20dbe_cosine(float_bits(radians), negative);
    return float_bits(rounded_mul(bits_float(cosine_bits), bits_float(multiplier_bits)));
}
