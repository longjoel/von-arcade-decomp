/* Semantic model of the SHARC opcode-0x1f endpoint-distance service. */

#include <math.h>

typedef unsigned int u32;

/* ADSP-2106x RSQRTS mantissa seed table, as used by the local SHARC core. */
static const u32 recovered_sharc_rsqrts_mantissa[128] = {
    0x00350000U, 0x00330000U, 0x00320000U, 0x00300000U,
    0x002f0000U, 0x002e0000U, 0x002d0000U, 0x002b0000U,
    0x002a0000U, 0x00290000U, 0x00280000U, 0x00270000U,
    0x00260000U, 0x00250000U, 0x00230000U, 0x00220000U,
    0x00210000U, 0x00200000U, 0x001f0000U, 0x001e0000U,
    0x001e0000U, 0x001d0000U, 0x001c0000U, 0x001b0000U,
    0x001a0000U, 0x00190000U, 0x00180000U, 0x00170000U,
    0x00160000U, 0x00160000U, 0x00150000U, 0x00140000U,
    0x00130000U, 0x00130000U, 0x00120000U, 0x00110000U,
    0x00100000U, 0x00100000U, 0x000f0000U, 0x000e0000U,
    0x000e0000U, 0x000d0000U, 0x000c0000U, 0x000b0000U,
    0x000b0000U, 0x000a0000U, 0x000a0000U, 0x00090000U,
    0x00080000U, 0x00080000U, 0x00070000U, 0x00070000U,
    0x00060000U, 0x00050000U, 0x00050000U, 0x00040000U,
    0x00040000U, 0x00030000U, 0x00030000U, 0x00020000U,
    0x00020000U, 0x00010000U, 0x00010000U, 0x00000000U,
    0x007f8000U, 0x007e0000U, 0x007c0000U, 0x007a0000U,
    0x00780000U, 0x00760000U, 0x00740000U, 0x00730000U,
    0x00710000U, 0x006f0000U, 0x006e0000U, 0x006c0000U,
    0x006a0000U, 0x00690000U, 0x00670000U, 0x00660000U,
    0x00640000U, 0x00630000U, 0x00620000U, 0x00600000U,
    0x005f0000U, 0x005e0000U, 0x005c0000U, 0x005b0000U,
    0x005a0000U, 0x00590000U, 0x00570000U, 0x00560000U,
    0x00550000U, 0x00540000U, 0x00530000U, 0x00520000U,
    0x00510000U, 0x004f0000U, 0x004e0000U, 0x004d0000U,
    0x004c0000U, 0x004b0000U, 0x004a0000U, 0x00490000U,
    0x00480000U, 0x00470000U, 0x00460000U, 0x00450000U,
    0x00450000U, 0x00440000U, 0x00430000U, 0x00420000U,
    0x00410000U, 0x00400000U, 0x003f0000U, 0x003e0000U,
    0x003e0000U, 0x003d0000U, 0x003c0000U, 0x003b0000U,
    0x003a0000U, 0x003a0000U, 0x00390000U, 0x00380000U,
    0x00370000U, 0x00370000U, 0x00360000U, 0x00350000U,
};

/* Reproduce the local SHARC core's RSQRTS seed, before Newton refinement. */
u32 recovered_sharc_rsqrts_seed(u32 bits)
{
    u32 exponent;
    int exponent_unbiased;
    int result_exponent;
    u32 mantissa;
    u32 sign;

    if (bits > 0x80000000U ||
        ((bits & 0x7f800000U) == 0x7f800000U &&
         (bits & 0x007fffffU) != 0U))
        return 0xffffffffU;

    exponent = (bits >> 23) & 0xffU;
    exponent_unbiased = (int)exponent - 127;
    /* C division truncates toward zero; SHARC/MAME uses arithmetic >> 1. */
    result_exponent = -(exponent_unbiased >= 0
                            ? exponent_unbiased / 2
                            : -((-exponent_unbiased + 1) / 2)) - 1;
    mantissa = bits & 0x00ffffffU;
    sign = bits & 0x80000000U;
    return sign |
           (((u32)(result_exponent + 127) & 0xffU) << 23) |
           recovered_sharc_rsqrts_mantissa[mantissa >> 17];
}

static float recovered_sharc_opcode_1f_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } input;

    input.bits = bits;
    return input.value;
}

static u32 recovered_sharc_opcode_1f_bits(float value)
{
    union {
        u32 bits;
        float value;
    } output;

    output.value = value;
    return output.bits;
}

/*
 * The FIFO supplies endpoint pairs (x0,x1), (y0,y1), and (z0,z1).
 * The ROM forms the three component differences, accumulates their squared
 * magnitude, and obtains the distance through the RSQRTS/refinement path.
 * The runtime probe confirms F0 = 169.0 for differences (3,4,12), followed
 * by an output immediately below 13.0 due to SHARC rounding.
 */
u32 recovered_sharc_opcode_1f_length(const u32 endpoints[6])
{
    float dx = recovered_sharc_opcode_1f_float(endpoints[0]) -
               recovered_sharc_opcode_1f_float(endpoints[1]);
    float dy = recovered_sharc_opcode_1f_float(endpoints[2]) -
               recovered_sharc_opcode_1f_float(endpoints[3]);
    float dz = recovered_sharc_opcode_1f_float(endpoints[4]) -
               recovered_sharc_opcode_1f_float(endpoints[5]);
    float squared = dx * dx + dy * dy + dz * dz;
    u32 squared_bits = recovered_sharc_opcode_1f_bits(squared);

    /* RSQRTS(0) seeds a non-finite refinement path; the observed result is
     * the SHARC canonical NaN rather than host sqrtf(0). */
    if (squared == 0.0f)
        return 0xffffffffU;

    /* 0x3fa..0x407: three rounds of r = .5*r*(3 - x*r*r), with each
     * multiply/subtract rounded as a 32-bit SHARC operation. */
    float r = recovered_sharc_opcode_1f_float(
        recovered_sharc_rsqrts_seed(squared_bits));
    for (int round = 0; round < 3; ++round) {
        float r2 = r * r;
        r2 = r2 * squared;
        r = 0.5f * r;
        r = r * (3.0f - r2);
    }
    return recovered_sharc_opcode_1f_bits(squared * r);
}
