/* Recovered state initializer for SHARC opcode 0x29. */
#include <math.h>
#include <stdint.h>

/*
 * The four FIFO words are translation[0..2] followed by a signed 16-bit
 * angle. The ROM resets the 3x3 state, then installs a row-major Y rotation
 * and preserves the translation tail. Helper rounding is represented by
 * host sin/cos here; the observed residuals remain qualified.
 */
void recovered_sharc_opcode_29_initialize(
    const float translation[3], int16_t angle_word, float matrix[9],
    float tail[3])
{
    const float radians_per_word = 3.14159265358979323846f / 32767.0f;
    float angle = (float)angle_word * radians_per_word;
    float sine = sinf(angle);
    float cosine = cosf(angle);

    matrix[0] = cosine;
    matrix[1] = 0.0f;
    matrix[2] = sine;
    matrix[3] = 0.0f;
    matrix[4] = 1.0f;
    matrix[5] = 0.0f;
    matrix[6] = -sine;
    matrix[7] = 0.0f;
    matrix[8] = cosine;
    tail[0] = translation[0];
    tail[1] = translation[1];
    tail[2] = translation[2];
}
