/* Recovered normal-case stateful division contract for SHARC opcode 0x35. */
#include <stdint.h>

/* ADSP-2106x RECIPS mantissa table, copied from MAME's SHARC core. */
static const uint32_t recips_mantissa[128] = {
    0x007f8000,0x007e0000,0x007c0000,0x007a0000,0x00780000,0x00760000,0x00740000,0x00720000,
    0x00700000,0x006f0000,0x006d0000,0x006b0000,0x006a0000,0x00680000,0x00660000,0x00650000,
    0x00630000,0x00610000,0x00600000,0x005e0000,0x005d0000,0x005b0000,0x005a0000,0x00590000,
    0x00570000,0x00560000,0x00540000,0x00530000,0x00520000,0x00500000,0x004f0000,0x004e0000,
    0x004c0000,0x004b0000,0x004a0000,0x00490000,0x00470000,0x00460000,0x00450000,0x00440000,
    0x00430000,0x00410000,0x00400000,0x003f0000,0x003e0000,0x003d0000,0x003c0000,0x003b0000,
    0x003a0000,0x00390000,0x00380000,0x00370000,0x00360000,0x00350000,0x00340000,0x00330000,0x00320000,
    0x00310000,0x00300000,0x002f0000,0x002e0000,0x002d0000,0x002c0000,0x002b0000,0x002a0000,
    0x00290000,0x00280000,0x00280000,0x00270000,0x00260000,0x00250000,0x00240000,0x00230000,
    0x00230000,0x00220000,0x00210000,0x00200000,0x001f0000,0x001f0000,0x001e0000,0x001d0000,
    0x001c0000,0x001c0000,0x001b0000,0x001a0000,0x00190000,0x00190000,0x00180000,0x00170000,
    0x00170000,0x00160000,0x00150000,0x00140000,0x00140000,0x00130000,0x00120000,0x00120000,
    0x00110000,0x00100000,0x00100000,0x000f0000,0x000f0000,0x000e0000,0x000d0000,0x000d0000,
    0x000c0000,0x000c0000,0x000b0000,0x000a0000,0x000a0000,0x00090000,0x00090000,0x00080000,
    0x00070000,0x00070000,0x00060000,0x00060000,0x00050000,0x00050000,0x00040000,0x00040000,
    0x00030000,0x00030000,0x00020000,0x00020000,0x00010000,0x00010000,0x00000000,
};

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

uint32_t recovered_sharc_recips_seed(uint32_t bits)
{
    uint32_t exponent = (bits >> 23) & 0xffU;
    int result_exponent;

    if (exponent == 0xffU && (bits & 0x007fffffU) != 0U)
        return 0xffffffffU;
    if ((bits & 0x7fffffffU) == 0U)
        return (bits & 0x80000000U) | 0x7f800000U;
    result_exponent = -((int)exponent - 127) - 1;
    if (result_exponent > 125 || result_exponent < -126)
        return bits & 0x80000000U;
    return (bits & 0x80000000U) |
           ((uint32_t)(result_exponent + 127) << 23) |
           recips_mantissa[(bits & 0x007fffffU) >> 16];
}

static float rounded_mul(float left, float right)
{
    volatile float result = left * right;
    return result;
}

static float rounded_sub(float left, float right)
{
    volatile float result = left - right;
    return result;
}

static float rounded_add(float left, float right)
{
    volatile float result = left + right;
    return result;
}

/*
 * The preceding handler supplies F0/F2/F13 state. The visible 0x35 path
 * forms (F0_previous*w0 + F2_previous*w2 + w4) / w5. Its RECIPS/Newton path
 * is reproduced with the SHARC seed table and visible multiply/correction
 * order. Exceptional and denormal behavior remains qualified.
 */
uint32_t recovered_sharc_opcode_35_divide(
    uint32_t previous_f0, uint32_t w0, uint32_t previous_f2,
    uint32_t w2, uint32_t w4, uint32_t w5)
{
    float numerator = rounded_mul(bits_float(previous_f0), bits_float(w0));
    float second = rounded_mul(bits_float(previous_f2), bits_float(w2));
    float denominator = bits_float(w5);
    float reciprocal = bits_float(recovered_sharc_recips_seed(w5));

    numerator = rounded_add(numerator, second);
    numerator = rounded_add(numerator, bits_float(w4));
    /* RECIPS(+-0) and the subsequent zero/infinity correction path produce
     * the SHARC canonical NaN. Infinity and NaN denominators likewise cannot
     * produce a finite quotient. */
    if ((w5 & 0x7fffffffU) == 0U ||
        (w5 & 0x7f800000U) == 0x7f800000U)
        return 0xffffffffU;
    /* The ROM keeps the quotient in F7 and the Newton residual in F12.
     * Updating the reciprocal completely and multiplying the numerator only
     * once at the end is algebraically equivalent, but not bit-equivalent:
     * each visible correction has its own 32-bit rounding boundary. */
    float quotient = rounded_mul(numerator, reciprocal);
    float residual = rounded_mul(reciprocal, denominator);
    for (int round = 0; round < 3; ++round) {
        float correction = rounded_sub(2.0f, residual);
        quotient = rounded_mul(quotient, correction);
        residual = rounded_mul(correction, residual);
    }
    return float_bits(quotient);
}
