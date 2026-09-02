/* Recovered packed translation and Euler-matrix rebuild for SHARC opcode 0x2e. */
#include <math.h>
#include <stdint.h>
#include <string.h>

static float recovered_sharc_opcode_2e_decode(uint32_t word)
{
    uint16_t half = (uint16_t)word;
    uint32_t bits = ((uint32_t)(half & 0x8000U) << 16)
                  | (((uint32_t)((half >> 10) & 0x1fU) + 112U) << 23)
                  | ((uint32_t)(half & 0x03ffU) << 13);
    float value;

    memcpy(&value, &bits, sizeof(value));
    return value;
}

/*
 * The six FIFO words are three low-16-bit packed coordinates followed by
 * three fields whose low signed byte is promoted by eight bits before the
 * shared signed-16 trig helpers. The matrix passes are Rx * Ry * Rz.
 * This intentionally preserves the ROM's no-special-case zero/denormal
 * behavior in the packed decoder.
 */
void recovered_sharc_opcode_2e_initialize(
    const uint32_t packed_translation[3], const uint32_t angle_fields[3],
    float matrix[9], float tail[3])
{
    const float radians_per_word = 3.14159265358979323846f / 32767.0f;
    const int16_t x_word = (int16_t)((int8_t)(angle_fields[0] & 0xffU) << 8);
    const int16_t y_word = (int16_t)((int8_t)(angle_fields[1] & 0xffU) << 8);
    const int16_t z_word = (int16_t)((int8_t)(angle_fields[2] & 0xffU) << 8);
    const float x = (float)x_word * radians_per_word;
    const float y = (float)y_word * radians_per_word;
    const float z = (float)z_word * radians_per_word;
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

    tail[0] = recovered_sharc_opcode_2e_decode(packed_translation[0]);
    tail[1] = recovered_sharc_opcode_2e_decode(packed_translation[1]);
    tail[2] = recovered_sharc_opcode_2e_decode(packed_translation[2]);
}
