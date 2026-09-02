/* Recovered projection transform for SHARC opcode 0x31. */
#include <math.h>
#include <stdint.h>

/*
 * R10 and R9 are signed-16 angle words. The final projection uses
 * Ry(-R10) * Rx(-R9), then adds the direct translation tail to M * vector,
 * where vector is R13/R14/R15. Intermediate state stores use a different
 * layout, so this function models the externally emitted projection.
 */
void recovered_sharc_opcode_31_project(
    const float tail[3], int16_t r10_angle, int16_t r9_angle,
    const float vector[3], float matrix[9], float output[3])
{
    const float radians_per_word = 3.14159265358979323846f / 32767.0f;
    const float y = (float)r10_angle * radians_per_word;
    const float x = (float)r9_angle * radians_per_word;
    const float sy = sinf(y), cy = cosf(y);
    const float sx = sinf(x), cx = cosf(x);

    matrix[0] = cy;
    matrix[1] = sy * sx;
    matrix[2] = -sy * cx;
    matrix[3] = 0.0f;
    matrix[4] = cx;
    matrix[5] = sx;
    matrix[6] = sy;
    matrix[7] = -cy * sx;
    matrix[8] = cy * cx;

    output[0] = tail[0] + matrix[0] * vector[0]
                       + matrix[1] * vector[1] + matrix[2] * vector[2];
    output[1] = tail[1] + matrix[3] * vector[0]
                       + matrix[4] * vector[1] + matrix[5] * vector[2];
    output[2] = tail[2] + matrix[6] * vector[0]
                       + matrix[7] * vector[1] + matrix[8] * vector[2];
}
