/* Proven affine portion of the SHARC opcode-0x22 projection service. */

#include <math.h>

typedef unsigned int u32;

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

/*
 * The ROM uses the same column-major affine state as opcode 0x1a.  This
 * helper deliberately stops before the fourth-input clip predicate and the
 * -1/-2 fallback selectors, which are a separate control layer.
 */
void recovered_sharc_opcode_22_affine(const u32 input[3],
                                      const u32 state[12],
                                      u32 output[3])
{
    float x = bits_float(input[0]);
    float y = bits_float(input[1]);
    float z = bits_float(input[2]);
    float s0 = bits_float(state[0]);
    float s1 = bits_float(state[1]);
    float s2 = bits_float(state[2]);
    float s3 = bits_float(state[3]);
    float s4 = bits_float(state[4]);
    float s5 = bits_float(state[5]);
    float s6 = bits_float(state[6]);
    float s7 = bits_float(state[7]);
    float s8 = bits_float(state[8]);
    float s9 = bits_float(state[9]);
    float s10 = bits_float(state[10]);
    float s11 = bits_float(state[11]);

    output[0] = float_bits((x * s2) + (y * s5) + (z * s8) + s11);
    output[1] = float_bits((x * s0) + (y * s3) + (z * s6) + s9);
    output[2] = float_bits((x * s1) + (y * s4) + (z * s7) + s10);
}

/*
 * Complete finite-path clip contract.  The six clip words are the two plane
 * coefficients followed by thresholds at offsets 2..5.  The ROM first
 * rejects negative affine depth with -2.0, then checks two signed pairs of
 * perspective-plane expressions and returns -1.0 on any failed comparison.
 * The normal path publishes the first affine component.
 */
int recovered_sharc_opcode_22_clipped(const u32 input[4],
                                      const u32 state[12],
                                      const u32 clip[6],
                                      u32 *output)
{
    u32 affine_input[3] = { input[0], input[1], input[2] };
    u32 affine_output[3];
    recovered_sharc_opcode_22_affine(affine_input, state, affine_output);

    float depth = bits_float(affine_output[0]);
    float b = bits_float(affine_output[1]);
    float c = bits_float(affine_output[2]);
    float w = bits_float(input[3]);
    float p = bits_float(clip[0]);
    float q = bits_float(clip[1]);
    float inv_depth = 1.0f / depth;

    if (depth < 0.0f) {
        *output = 0xc0000000U;
        return -2;
    }

    /* RECIPS(0) is +infinity on SHARC; its first correction multiplies
     * infinity by the zero depth, making all four clip comparisons unordered.
     * A NaN depth follows the same fall-through path. */
    if (depth == 0.0f || isnan(depth)) {
        *output = affine_output[0];
        return 0;
    }

    if (((q * c - p * w) * inv_depth) >= bits_float(clip[4]) ||
        ((q * c + q * w) * inv_depth) <= bits_float(clip[5]) ||
        ((p * b - p * w) * inv_depth) >= bits_float(clip[2]) ||
        ((p * b + q * w) * inv_depth) <= bits_float(clip[3])) {
        *output = 0xbf800000U;
        return -1;
    }

    *output = affine_output[0];
    return 0;
}
