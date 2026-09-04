/* Recovered contract for SHARC opcode 0x1e at 0x203dc. */
#include <stdint.h>

typedef unsigned int u32;
#include "recovered_float.h"

extern u32 recovered_sharc_helper_20dbe_cosine(u32 magnitude, int negative);

/* The first word is a signed half-turn angle; the delayed R15 word is F15. */
u32 recovered_sharc_opcode_1e(u32 angle_word, u32 multiplier_bits)
{
    int16_t signed_angle = (int16_t)(angle_word & 0xffffU);
    int negative = signed_angle < 0;
    int magnitude_word = negative ? -(int)signed_angle : (int)signed_angle;
    float radians = recovered_rounded_mul((float)magnitude_word, recovered_float_from_bits(0x38c9116d));
    u32 cosine_bits = recovered_sharc_helper_20dbe_cosine(recovered_float_to_bits(radians), negative);
    return recovered_float_to_bits(recovered_rounded_mul(recovered_float_from_bits(cosine_bits), recovered_float_from_bits(multiplier_bits)));
}
