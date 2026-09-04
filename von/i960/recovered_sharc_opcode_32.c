/* Recovered angle/translation contract for SHARC opcode 0x32. */
#include <math.h>
#include <stdint.h>
#include "recovered_float.h"

/*
 * The direct R0/R1/R2 translation and the three live angle fields are cleanly
 * recoverable. The ROM applies Y(R3), then Z(R5), then X(R6), equivalent to
 * left multiplication by Rx * Rz * Ry. Other retained fields in this
 * stateful handler are intentionally not guessed here.
 */
void recovered_sharc_opcode_32_initialize(
    const float translation[3], const int16_t angle_words[3],
    float matrix[9], float tail[3])
{
    const float radians_per_word = 3.14159265358979323846f / 32767.0f;
    const float y = (float)angle_words[0] * radians_per_word;
    const float z = (float)angle_words[1] * radians_per_word;
    const float x = (float)angle_words[2] * radians_per_word;

    recovered_rotate_y(matrix, sinf(y), cosf(y));
    recovered_rotate_z(matrix, sinf(z), cosf(z));
    recovered_rotate_x(matrix, sinf(x), cosf(x));
    tail[0] = translation[0];
    tail[1] = translation[1];
    tail[2] = translation[2];
}
