/* Recovered normal finite contracts for SHARC opcodes 0x03 and 0x04. */
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

extern u32 recovered_sharc_recips_seed(u32 bits);

static float refined_quotient(float numerator, float denominator)
{
    float reciprocal = bits_float(recovered_sharc_recips_seed(float_bits(denominator)));
    float quotient = rounded_mul(reciprocal, numerator);
    float product = rounded_mul(reciprocal, denominator);

    /* Matches the three visible F12/F7/F0 correction groups and the final
     * F0 = F0 * F7 delayed arithmetic boundary. */
    for (int round = 0; round < 3; ++round)
    {
        float correction = 2.0f - product;
        quotient = rounded_mul(quotient, correction);
        product = rounded_mul(product, correction);
    }
    return quotient;
}

/* Opcode 0x03: numerator / denominator, using the ROM RECIPS schedule. */
u32 recovered_sharc_opcode_03_reciprocal(u32 numerator_bits, u32 denominator_bits)
{
    return float_bits(refined_quotient(bits_float(numerator_bits), bits_float(denominator_bits)));
}

/* Opcode 0x04: numerator - (numerator / denominator) * denominator. */
u32 recovered_sharc_opcode_04_residual(u32 numerator_bits, u32 denominator_bits)
{
    float numerator = bits_float(numerator_bits);
    float denominator = bits_float(denominator_bits);
    float quotient = refined_quotient(numerator, denominator);
    return float_bits(numerator - rounded_mul(quotient, denominator));
}
