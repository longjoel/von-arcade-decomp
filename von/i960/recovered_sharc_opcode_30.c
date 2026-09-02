/* Recovered translation update and scaled-Z rebuild for SHARC opcode 0x30. */
#include <math.h>
#include <stdint.h>

/*
 * The first pass publishes v^T * prior_matrix into the translation tail.
 * State is then rebuilt as R13 * Rz(R15), where R13 is a direct float and
 * R15 is a signed-16 angle. Host sin/cos stand in for the ROM helper pair;
 * helper rounding leaves small residuals at exact quarter turns.
 */
void recovered_sharc_opcode_30_update(
    const float translation[3], const float prior_matrix[9], float scalar,
    int16_t angle_word, float matrix[9], float tail[3])
{
    const float radians_per_word = 3.14159265358979323846f / 32767.0f;
    const float angle = (float)angle_word * radians_per_word;
    const float sine = sinf(angle);
    const float cosine = cosf(angle);

    tail[0] = translation[0] * prior_matrix[0]
            + translation[1] * prior_matrix[3]
            + translation[2] * prior_matrix[6];
    tail[1] = translation[0] * prior_matrix[1]
            + translation[1] * prior_matrix[4]
            + translation[2] * prior_matrix[7];
    tail[2] = translation[0] * prior_matrix[2]
            + translation[1] * prior_matrix[5]
            + translation[2] * prior_matrix[8];

    matrix[0] = scalar * cosine;
    matrix[1] = -scalar * sine;
    matrix[2] = 0.0f;
    matrix[3] = scalar * sine;
    matrix[4] = scalar * cosine;
    matrix[5] = 0.0f;
    matrix[6] = 0.0f;
    matrix[7] = 0.0f;
    matrix[8] = scalar;
}
