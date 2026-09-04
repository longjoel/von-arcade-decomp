/* Recovered contract for SHARC opcode 0x1c at 0x203c2. */
#include <stdint.h>
#include "recovered_float.h"

typedef uint32_t u32;

extern u32 recovered_sharc_helper_20dbe_cosine(u32 magnitude, int negative);

/* The cosine helper uses the same signed 16-bit angle convention. */
u32 recovered_sharc_opcode_1c(u32 angle_word)
{
    int16_t signed_angle = (int16_t)(angle_word & 0xffffU);
    int negative = signed_angle < 0;
    int magnitude_word = negative ? -(int)signed_angle : (int)signed_angle;
    float radians = recovered_rounded_mul((float)magnitude_word,
                                recovered_float_from_bits(0x38c9116d));
    /* The standalone helper model exposes the post-staging radian contract. */
    return recovered_sharc_helper_20dbe_cosine(recovered_float_to_bits(radians), negative);
}
