/* Recovered contract for SHARC opcode 0x1c at 0x203c2. */
#include <stdint.h>

typedef uint32_t u32;

static float bits_float(u32 bits)
{
    union { u32 bits; float value; } value;
    value.bits = bits;
    return value.value;
}

static u32 float_bits(float value)
{
    union { u32 bits; float value; } result;
    result.value = value;
    return result.bits;
}

static float rounded_mul(float left, float right)
{
    volatile float result = left * right;
    return result;
}

extern u32 recovered_sharc_helper_20dbe_cosine(u32 magnitude, int negative);

/* The cosine helper uses the same signed 16-bit angle convention. */
u32 recovered_sharc_opcode_1c(u32 angle_word)
{
    int16_t signed_angle = (int16_t)(angle_word & 0xffffU);
    int negative = signed_angle < 0;
    int magnitude_word = negative ? -(int)signed_angle : (int)signed_angle;
    float radians = rounded_mul((float)magnitude_word,
                                bits_float(0x38c9116d));
    /* The standalone helper model exposes the post-staging radian contract. */
    return recovered_sharc_helper_20dbe_cosine(float_bits(radians), negative);
}
