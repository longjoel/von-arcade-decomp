/* Recovered packed-coordinate and Euler-state service for SHARC opcode 0x42. */
#include <math.h>
#include <stdint.h>
#include <string.h>

static float recovered_sharc_opcode_42_decode(uint32_t word)
{
    uint16_t packed = (uint16_t)word;
    uint32_t bits = ((uint32_t)(packed & 0x8000U) << 16)
                  | (((uint32_t)((packed >> 10) & 0x1fU) + 112U) << 23)
                  | ((uint32_t)(packed & 0x03ffU) << 13);
    float value;

    memcpy(&value, &bits, sizeof(value));
    return value;
}

/*
 * The opening 0x42 pass decodes R0/R1/R2 and projects them through the
 * persistent row-major state matrix.  The ROM stores these three values in
 * state slots 9..11 before the angle-dependent passes rewrite matrix entries.
 * This deliberately does not model those later multi-pass mutations.
 */
void recovered_sharc_opcode_42_first_pass(
    const uint32_t packed_vector[3], const float matrix[9], float output[3])
{
    const float x = recovered_sharc_opcode_42_decode(packed_vector[0]);
    const float y = recovered_sharc_opcode_42_decode(packed_vector[1]);
    const float z = recovered_sharc_opcode_42_decode(packed_vector[2]);

    output[0] = x * matrix[0] + y * matrix[3] + z * matrix[6];
    output[1] = x * matrix[1] + y * matrix[4] + z * matrix[7];
    output[2] = x * matrix[2] + y * matrix[5] + z * matrix[8];
}

/*
 * Apply the three in-place row rotations used by the ROM. The Z, Y, and X
 * passes update the corresponding row pairs in that order, equivalent to
 * left multiplication by Rx * Ry * Rz. The tail is projected by the incoming
 * matrix before those state updates, matching the opening pass above.
 */
void recovered_sharc_opcode_42_initialize(
    const uint32_t packed_vector[3], const int16_t angle_words[3],
    float matrix[9], float tail[3])
{
    const float radians_per_word = 3.14159265358979323846f / 32767.0f;
    const float x = (float)angle_words[0] * radians_per_word;
    const float y = (float)angle_words[1] * radians_per_word;
    const float z = (float)angle_words[2] * radians_per_word;
    const float sx = sinf(x), cx = cosf(x);
    const float sy = sinf(y), cy = cosf(y);
    const float sz = sinf(z), cz = cosf(z);
    float original[9];

    memcpy(original, matrix, sizeof(original));
    recovered_sharc_opcode_42_first_pass(packed_vector, original, tail);

    /* Z rotation: rows 0 and 1. */
    matrix[0] = cz * original[0] - sz * original[3];
    matrix[1] = cz * original[1] - sz * original[4];
    matrix[2] = cz * original[2] - sz * original[5];
    matrix[3] = sz * original[0] + cz * original[3];
    matrix[4] = sz * original[1] + cz * original[4];
    matrix[5] = sz * original[2] + cz * original[5];
    matrix[6] = original[6];
    matrix[7] = original[7];
    matrix[8] = original[8];

    /* Y rotation: rows 0 and 2, using the post-Z state. */
    {
        float row0[3] = { matrix[0], matrix[1], matrix[2] };
        float row2[3] = { matrix[6], matrix[7], matrix[8] };
        for (unsigned column = 0; column < 3; ++column) {
            matrix[column] = cy * row0[column] + sy * row2[column];
            matrix[6 + column] = -sy * row0[column] + cy * row2[column];
        }
    }

    /* X rotation: rows 1 and 2, using the post-Y state. */
    {
        float row1[3] = { matrix[3], matrix[4], matrix[5] };
        float row2[3] = { matrix[6], matrix[7], matrix[8] };
        for (unsigned column = 0; column < 3; ++column) {
            matrix[3 + column] = cx * row1[column] - sx * row2[column];
            matrix[6 + column] = sx * row1[column] + cx * row2[column];
        }
    }
}
