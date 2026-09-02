/* Recovered translation and Euler-matrix rebuild for SHARC opcode 0x2c. */
#include <math.h>
#include <stdint.h>

/*
 * The six FIFO words are three direct float translation values followed by
 * signed 16-bit X, Y, and Z angle words. The ROM's rebuild passes are
 * equivalent, at host precision, to the row-major product Rx * Ry * Rz.
 * SHARC helper rounding leaves small residuals near exact quarter turns.
 */
void recovered_sharc_opcode_2c_initialize(
    const float translation[3], const int16_t angle_words[3], float matrix[9],
    float tail[3])
{
    const float radians_per_word = 3.14159265358979323846f / 32767.0f;
    const float x = (float)angle_words[0] * radians_per_word;
    const float y = (float)angle_words[1] * radians_per_word;
    const float z = (float)angle_words[2] * radians_per_word;
    const float sx = sinf(x), cx = cosf(x);
    const float sy = sinf(y), cy = cosf(y);
    const float sz = sinf(z), cz = cosf(z);

    matrix[0] = cy * cz;
    matrix[1] = -cy * sz;
    matrix[2] = sy;
    matrix[3] = sx * sy * cz + cx * sz;
    matrix[4] = -sx * sy * sz + cx * cz;
    matrix[5] = -sx * cy;
    matrix[6] = -cx * sy * cz + sx * sz;
    matrix[7] = cx * sy * sz + sx * cz;
    matrix[8] = cx * cy;

    tail[0] = translation[0];
    tail[1] = translation[1];
    tail[2] = translation[2];
}
