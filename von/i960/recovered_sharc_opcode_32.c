/* Recovered angle/translation contract for SHARC opcode 0x32. */
#include <math.h>
#include <stdint.h>

static void rotate_y(float matrix[9], float sine, float cosine)
{
    for (unsigned column = 0; column < 3; ++column) {
        float row0 = matrix[column];
        float row2 = matrix[6 + column];
        matrix[column] = cosine * row0 + sine * row2;
        matrix[6 + column] = -sine * row0 + cosine * row2;
    }
}

static void rotate_z(float matrix[9], float sine, float cosine)
{
    for (unsigned column = 0; column < 3; ++column) {
        float row0 = matrix[column];
        float row1 = matrix[3 + column];
        matrix[column] = cosine * row0 - sine * row1;
        matrix[3 + column] = sine * row0 + cosine * row1;
    }
}

static void rotate_x(float matrix[9], float sine, float cosine)
{
    for (unsigned column = 0; column < 3; ++column) {
        float row1 = matrix[3 + column];
        float row2 = matrix[6 + column];
        matrix[3 + column] = cosine * row1 - sine * row2;
        matrix[6 + column] = sine * row1 + cosine * row2;
    }
}

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

    rotate_y(matrix, sinf(y), cosf(y));
    rotate_z(matrix, sinf(z), cosf(z));
    rotate_x(matrix, sinf(x), cosf(x));
    tail[0] = translation[0];
    tail[1] = translation[1];
    tail[2] = translation[2];
}
