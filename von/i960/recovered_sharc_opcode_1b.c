/* Recovered contract for SHARC opcode 0x1b at 0x203b6. */
#include <stdint.h>

typedef uint32_t u32;
#include "recovered_float.h"

extern u32 recovered_sharc_helper_20dc4_sine(u32 magnitude, int negative);

/* The FIFO word is a signed 16-bit fixed-point angle. */
u32 recovered_sharc_opcode_1b(u32 angle_word)
{
    int16_t signed_angle = (int16_t)(angle_word & 0xffffU);
    int negative = signed_angle < 0;
    int magnitude_word = negative ? -(int)signed_angle : (int)signed_angle;
    float radians = recovered_rounded_mul((float)magnitude_word,
                                recovered_float_from_bits(0x38c9116d));
    /* The standalone helper model exposes the post-staging radian contract. */
    return recovered_sharc_helper_20dc4_sine(recovered_float_to_bits(radians), negative);
}
