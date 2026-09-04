/* Semantic model of the SHARC opcode-0x0b normalized cross-product service. */

#include <math.h>
#include "recovered_float.h"

typedef unsigned int u32;

extern u32 recovered_sharc_rsqrts_seed(u32 bits);

static float rsqrt(float value)
{
    float r = recovered_float_from_bits(recovered_sharc_rsqrts_seed(recovered_float_to_bits(value)));
    for (int round = 0; round < 3; ++round) {
        float r2 = r * r;
        r2 = r2 * value;
        r = 0.5f * r;
        r = r * (3.0f - r2);
    }
    return r;
}

void recovered_sharc_opcode_0b_normalized_cross(const u32 input[9], u32 output[3])
{
    float ax = recovered_float_from_bits(input[0]);
    float ay = recovered_float_from_bits(input[1]);
    float az = recovered_float_from_bits(input[2]);
    float bx = recovered_float_from_bits(input[3]);
    float by = recovered_float_from_bits(input[4]);
    float bz = recovered_float_from_bits(input[5]);
    float ex = recovered_float_from_bits(input[6]);
    float ey = recovered_float_from_bits(input[7]);
    /* The ninth FIFO read at 0x2022c overwrites R8 after the arithmetic
     * operands have been formed; it is consumed but does not affect this
     * recovered finite path. */
    float dx = ax - bx;
    float dy = ay - by;
    float dz = az - bz;
    float x = (dy * 0.0f) - (dz * ey);
    float y = (dz * ex) - (dx * 0.0f);
    float z = (dx * ey) - (dy * ex);
    float squared = x * x + y * y + z * z;
    if (isnan(squared) || isinf(squared) || squared == 0.0f) {
        /* Status-aware, dispatcher-aligned MAME probes confirm canonical NaN
         * for zero, NaN, infinity, and denormal edge packets. */
        output[0] = 0xffffffffU;
        output[1] = 0xffffffffU;
        output[2] = 0xffffffffU;
        return;
    }
    float scale = rsqrt(squared);
    output[0] = recovered_float_to_bits(x * scale);
    output[1] = recovered_float_to_bits(y * scale);
    output[2] = recovered_float_to_bits(z * scale);
}
