/* Recovered normal finite contracts for SHARC opcodes 0x03 and 0x04. */
#include <stdint.h>
#include "recovered_float.h"

typedef unsigned int u32;

extern u32 recovered_sharc_recips_seed(u32 bits);

static float refined_quotient(float numerator, float denominator)
{
    float reciprocal = recovered_float_from_bits(recovered_sharc_recips_seed(recovered_float_to_bits(denominator)));
    float quotient = recovered_rounded_mul(reciprocal, numerator);
    float product = recovered_rounded_mul(reciprocal, denominator);

    /* Matches the three visible F12/F7/F0 correction groups and the final
     * F0 = F0 * F7 delayed arithmetic boundary. */
    for (int round = 0; round < 3; ++round)
    {
        float correction = 2.0f - product;
        quotient = recovered_rounded_mul(quotient, correction);
        product = recovered_rounded_mul(product, correction);
    }
    return quotient;
}

/* Opcode 0x03: numerator / denominator, using the ROM RECIPS schedule. */
u32 recovered_sharc_opcode_03_reciprocal(u32 numerator_bits, u32 denominator_bits)
{
    return recovered_float_to_bits(refined_quotient(recovered_float_from_bits(numerator_bits), recovered_float_from_bits(denominator_bits)));
}

/* Opcode 0x04: numerator - (numerator / denominator) * denominator. */
u32 recovered_sharc_opcode_04_residual(u32 numerator_bits, u32 denominator_bits)
{
    float numerator = recovered_float_from_bits(numerator_bits);
    float denominator = recovered_float_from_bits(denominator_bits);
    float quotient = refined_quotient(numerator, denominator);
    return recovered_float_to_bits(numerator - recovered_rounded_mul(quotient, denominator));
}
