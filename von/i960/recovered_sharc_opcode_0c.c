/* Semantic model of the SHARC opcode-0x0c three-input normalizer. */

#include <math.h>
#include "recovered_float.h"

typedef unsigned int u32;

/* Shared with the opcode-0x1f model; both services use the same SHARC seed. */
extern u32 recovered_sharc_rsqrts_seed(u32 bits);

static int recovered_sharc_opcode_0c_is_nan(u32 bits)
{
    return (bits & 0x7f800000U) == 0x7f800000U &&
           (bits & 0x007fffffU) != 0U;
}

static int recovered_sharc_opcode_0c_is_infinity(u32 bits)
{
    return (bits & 0x7fffffffU) == 0x7f800000U;
}

static int recovered_sharc_opcode_0c_is_denormal(u32 bits)
{
    return (bits & 0x7f800000U) == 0U &&
           (bits & 0x007fffffU) != 0U;
}

static float recovered_sharc_opcode_0c_rsqrt(float value)
{
    u32 bits = recovered_float_to_bits(value);
    float r = recovered_float_from_bits(recovered_sharc_rsqrts_seed(bits));

    for (int round = 0; round < 3; ++round) {
        float r2 = r * r;
        r2 = r2 * value;
        r = 0.5f * r;
        r = r * (3.0f - r2);
    }
    return r;
}

void recovered_sharc_opcode_0c_normalize(const u32 input[3], u32 output[3])
{
    float x = recovered_float_from_bits(input[0]);
    float y = recovered_float_from_bits(input[1]);
    float z = recovered_float_from_bits(input[2]);
    float arithmetic_x = recovered_sharc_opcode_0c_is_denormal(input[0])
        ? recovered_float_from_bits(input[0] & 0x80000000U) : x;
    float arithmetic_y = recovered_sharc_opcode_0c_is_denormal(input[1])
        ? recovered_float_from_bits(input[1] & 0x80000000U) : y;
    float arithmetic_z = recovered_sharc_opcode_0c_is_denormal(input[2])
        ? recovered_float_from_bits(input[2] & 0x80000000U) : z;

    if (recovered_sharc_opcode_0c_is_nan(input[0]) ||
        recovered_sharc_opcode_0c_is_nan(input[1]) ||
        recovered_sharc_opcode_0c_is_nan(input[2])) {
        output[0] = 0xffffffffU;
        output[1] = 0xffffffffU;
        output[2] = 0xffffffffU;
        return;
    }

    /* MAME's SHARC RSQRTS(+inf) path seeds 0x1f800000.  Preserve the
     * infinite lanes and use that raw seed for finite lanes; this is the
     * observed service boundary, not an IEEE normalization rule. */
    if (recovered_sharc_opcode_0c_is_infinity(input[0]) ||
        recovered_sharc_opcode_0c_is_infinity(input[1]) ||
        recovered_sharc_opcode_0c_is_infinity(input[2])) {
        const float infinity_seed = recovered_float_from_bits(0x1f800000U);
        const u32 values[3] = { input[0], input[1], input[2] };
        const float lanes[3] = { x, y, z };
        for (int lane = 0; lane < 3; ++lane) {
            if (recovered_sharc_opcode_0c_is_infinity(values[lane]))
                output[lane] = values[lane];
            else
                output[lane] = recovered_float_to_bits(lanes[lane] * infinity_seed);
        }
        return;
    }

    float squared = arithmetic_x * arithmetic_x + arithmetic_y * arithmetic_y +
                    arithmetic_z * arithmetic_z;

    if (squared == 0.0f) {
        output[0] = 0xffffffffU;
        output[1] = 0xffffffffU;
        output[2] = 0xffffffffU;
        return;
    }

    float reciprocal_length = recovered_sharc_opcode_0c_rsqrt(squared);
    output[0] = recovered_float_to_bits(x * reciprocal_length);
    output[1] = recovered_float_to_bits(y * reciprocal_length);
    output[2] = recovered_float_to_bits(z * reciprocal_length);
}
