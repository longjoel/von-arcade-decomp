/* Recovered angle/translation contract for SHARC opcode 0x33. */
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
 * The ROM consumes R0/R1/R2 as direct translation values, then applies the
 * signed-16 R14 Y angle followed by the signed-16 R13 X angle. The interleaved
 * stores are an implementation detail of the same left multiplication
 * Rx(R13) * Ry(R14); the SHARC helper contributes small cosine residuals.
 */
void recovered_sharc_opcode_33_initialize(
    const float translation[3], const int16_t angle_words[2],
    float matrix[9], float tail[3])
{
    const float radians_per_word = 3.14159265358979323846f / 32767.0f;
    const float y = (float)angle_words[0] * radians_per_word;
    const float x = (float)angle_words[1] * radians_per_word;

    rotate_y(matrix, sinf(y), cosf(y));
    rotate_x(matrix, sinf(x), cosf(x));
    tail[0] = translation[0];
    tail[1] = translation[1];
    tail[2] = translation[2];
}
