/* Recovered two-vector/angle contract for SHARC opcode 0x34. */
#include <math.h>
#include <stdint.h>
#include "recovered_float.h"

static void add_matrix_vector(float tail[3], const float matrix[9], const float vector[3])
{
    for (unsigned row = 0; row < 3; ++row) {
        tail[row] += matrix[3 * row] * vector[0]
                  + matrix[3 * row + 1] * vector[1]
                  + matrix[3 * row + 2] * vector[2];
    }
}

/*
 * R0/R1/R2 contribute through the incoming matrix. The ROM then applies the
 * signed-16 R5 Y angle and R6 X angle, and contributes R13/R14/R15 through the
 * updated matrix. This is equivalent to Rx(R6) * Ry(R5) for the matrix, with
 * the two matrix-vector accumulations occurring on opposite sides of it.
 */
void recovered_sharc_opcode_34_initialize(
    const float first_vector[3], const int16_t angle_words[2],
    const float second_vector[3], float matrix[9], float tail[3])
{
    const float radians_per_word = 3.14159265358979323846f / 32767.0f;
    const float y = (float)angle_words[0] * radians_per_word;
    const float x = (float)angle_words[1] * radians_per_word;

    add_matrix_vector(tail, matrix, first_vector);
    recovered_rotate_y(matrix, sinf(y), cosf(y));
    recovered_rotate_x(matrix, sinf(x), cosf(x));
    add_matrix_vector(tail, matrix, second_vector);
}
