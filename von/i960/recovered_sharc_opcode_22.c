/* Proven affine portion of the SHARC opcode-0x22 projection service. */

#include <math.h>
#include "recovered_float.h"

typedef unsigned int u32;

/*
 * The ROM uses the same column-major affine state as opcode 0x1a.  This
 * helper deliberately stops before the fourth-input clip predicate and the
 * -1/-2 fallback selectors, which are a separate control layer.
 */
void recovered_sharc_opcode_22_affine(const u32 input[3],
                                      const u32 state[12],
                                      u32 output[3])
{
    float x = recovered_float_from_bits(input[0]);
    float y = recovered_float_from_bits(input[1]);
    float z = recovered_float_from_bits(input[2]);
    float s0 = recovered_float_from_bits(state[0]);
    float s1 = recovered_float_from_bits(state[1]);
    float s2 = recovered_float_from_bits(state[2]);
    float s3 = recovered_float_from_bits(state[3]);
    float s4 = recovered_float_from_bits(state[4]);
    float s5 = recovered_float_from_bits(state[5]);
    float s6 = recovered_float_from_bits(state[6]);
    float s7 = recovered_float_from_bits(state[7]);
    float s8 = recovered_float_from_bits(state[8]);
    float s9 = recovered_float_from_bits(state[9]);
    float s10 = recovered_float_from_bits(state[10]);
    float s11 = recovered_float_from_bits(state[11]);

    output[0] = recovered_float_to_bits((x * s2) + (y * s5) + (z * s8) + s11);
    output[1] = recovered_float_to_bits((x * s0) + (y * s3) + (z * s6) + s9);
    output[2] = recovered_float_to_bits((x * s1) + (y * s4) + (z * s7) + s10);
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

    float depth = recovered_float_from_bits(affine_output[0]);
    float b = recovered_float_from_bits(affine_output[1]);
    float c = recovered_float_from_bits(affine_output[2]);
    float w = recovered_float_from_bits(input[3]);
    float p = recovered_float_from_bits(clip[0]);
    float q = recovered_float_from_bits(clip[1]);
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

    if (((q * c - p * w) * inv_depth) >= recovered_float_from_bits(clip[4]) ||
        ((q * c + q * w) * inv_depth) <= recovered_float_from_bits(clip[5]) ||
        ((p * b - p * w) * inv_depth) >= recovered_float_from_bits(clip[2]) ||
        ((p * b + q * w) * inv_depth) <= recovered_float_from_bits(clip[3])) {
        *output = 0xbf800000U;
        return -1;
    }

    *output = affine_output[0];
    return 0;
}
