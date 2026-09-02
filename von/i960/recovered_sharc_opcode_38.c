/* Recovered packed-vector projection for SHARC opcode 0x38. */
#include <stdint.h>
#include <string.h>

static float recovered_sharc_opcode_38_decode(uint32_t word)
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
 * Decode three low-16-bit binary16-shaped coordinates and apply the
 * row-vector v^T * M convention used by the ROM's coefficient groups.
 */
void recovered_sharc_opcode_38_project(
    const uint32_t packed_vector[3], const float matrix[9], float output[3])
{
    const float x = recovered_sharc_opcode_38_decode(packed_vector[0]);
    const float y = recovered_sharc_opcode_38_decode(packed_vector[1]);
    const float z = recovered_sharc_opcode_38_decode(packed_vector[2]);

    output[0] = x * matrix[0] + y * matrix[3] + z * matrix[6];
    output[1] = x * matrix[1] + y * matrix[4] + z * matrix[7];
    output[2] = x * matrix[2] + y * matrix[5] + z * matrix[8];
}
