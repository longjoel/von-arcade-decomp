/* Recovered normal/degenerate state update for SHARC opcode 0x3d. */
#include <math.h>
#include <stdint.h>

static uint32_t float_bits(float value)
{
    union { float value; uint32_t bits; } converted = { value };
    return converted.bits;
}

/* Opcode 0x3d stores the transposed frame convention used by its sibling. */
void recovered_sharc_opcode_3d_frame(float x, float y, float z,
                                     uint32_t state[12])
{
    float horizontal = sqrtf(x * x + z * z);
    float length = sqrtf(x * x + y * y + z * z);

    if (horizontal == 0.0f || length == 0.0f ||
        isnan(horizontal) || isnan(length)) {
        for (unsigned index = 0; index < 9; ++index)
            state[index] = UINT32_C(0xffffffff);
        for (unsigned index = 9; index < 12; ++index)
            state[index] = 0;
        return;
    }

    state[0] = float_bits(z / horizontal);
    state[1] = float_bits(0.0f);
    state[2] = float_bits(-x / horizontal);
    state[3] = float_bits(-x * y / (length * horizontal));
    state[4] = float_bits(horizontal / length);
    state[5] = float_bits(-z * y / (length * horizontal));
    state[6] = float_bits(x / length);
    state[7] = float_bits(y / length);
    state[8] = float_bits(z / length);
    state[9] = state[10] = state[11] = 0;
}
