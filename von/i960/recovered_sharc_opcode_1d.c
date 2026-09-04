/* Recovered contract for SHARC opcode 0x1d at 0x203ce. */
#include <stdint.h>
#include <math.h>
#include "recovered_float.h"

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
    float radians = recovered_rounded_mul((float)magnitude_word, recovered_float_from_bits(0x38c9116d));
    uint32_t sine_bits = recovered_sharc_helper_20dc4_sine(recovered_float_to_bits(radians), negative);
    return recovered_float_to_bits(recovered_rounded_mul(recovered_float_from_bits(sine_bits), recovered_float_from_bits(multiplier_bits)));
}
