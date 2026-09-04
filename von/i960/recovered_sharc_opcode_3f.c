/* Recovered normal-case contract for SHARC opcode 0x3f. */
#include <math.h>
#include <stdint.h>
#include "recovered_float.h"

static int32_t signed_word(uint32_t word)
{
    return (int32_t)word;
}

/*
 * A and B are integer words, C is an IEEE single carried in F4, and D is the
 * delayed F12 input. The ROM computes D + C*(float(A)/float(B)); its RECIPS
 * refinement and exceptional saturation are intentionally outside this libm-
 * independent normal-case model.
 */
uint32_t recovered_sharc_opcode_3f_followup(const uint32_t input[4])
{
    int32_t a_word = signed_word(input[0]);
    int32_t b_word = signed_word(input[1]);
    float c = recovered_float_from_bits(input[2]);
    float d = recovered_float_from_bits(input[3]);

    /* These are the observed ROM boundaries of the RECIPS/FPU path. */
    if (isnan(c))
        return UINT32_C(0xffffffff);
    if (isinf(c) && c > 0.0f)
        return UINT32_C(0x7f7fffff);
    if (b_word == 0 && (a_word == 0 || a_word == 1))
        return UINT32_C(0xffffffff);

    return recovered_float_to_bits(d + c * ((float)a_word / (float)b_word));
}
