/* Proven frame-transpose update for SHARC opcode 0x24. */

typedef unsigned int u32;
#include "recovered_float.h"

extern u32 recovered_sharc_rsqrts_seed(u32 bits);

static float rsqrt(float value)
{
    float estimate = recovered_float_from_bits(recovered_sharc_rsqrts_seed(recovered_float_to_bits(value)));
    for (int round = 0; round < 3; ++round) {
        float square = estimate * estimate;
        square = square * value;
        estimate = 0.5f * estimate;
        estimate = estimate * (3.0f - square);
    }
    return estimate;
}

/*
 * Opcode 0x24 uses the transpose of opcode 0x23's Y-up frame.  As with the
 * neighboring service, state words are column-major and the update is a
 * post-multiply.  The x=z=0 NaN path is intentionally left to the SHARC
 * implementation because its payload is architecture-specific.
 */
void recovered_sharc_opcode_24_update_state(const u32 input[3],
                                             const u32 state[9],
                                             u32 output[9])
{
    float x = recovered_float_from_bits(input[0]);
    float y = recovered_float_from_bits(input[1]);
    float z = recovered_float_from_bits(input[2]);
    float squared = (x * x) + (y * y) + (z * z);
    float scale = rsqrt(squared);
    float nx = x * scale;
    float ny = y * scale;
    float nz = z * scale;
    float horizontal = rsqrt((nx * nx) + (nz * nz));
    float frame[3][3] = {
        { nz * horizontal, -nx * ny * horizontal, nx },
        { 0.0f,            1.0f / horizontal,       ny },
        { -nx * horizontal, -nz * ny * horizontal, nz },
    };

    for (int row = 0; row < 3; ++row) {
        float old_row[3] = {
            recovered_float_from_bits(state[row]),
            recovered_float_from_bits(state[row + 3]),
            recovered_float_from_bits(state[row + 6]),
        };
        for (int column = 0; column < 3; ++column) {
            output[row + (column * 3)] = recovered_float_to_bits(
                (old_row[0] * frame[0][column]) +
                (old_row[1] * frame[1][column]) +
                (old_row[2] * frame[2][column]));
        }
    }
}
