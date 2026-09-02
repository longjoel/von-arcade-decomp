/* Recovered row-major matrix projection for SHARC opcode 0x43. */
#include <stdint.h>

static float bits_float(uint32_t bits)
{
    union { uint32_t bits; float value; } converted = { bits };
    return converted.value;
}

static uint32_t float_bits(float value)
{
    union { float value; uint32_t bits; } converted = { value };
    return converted.bits;
}

/* The ROM emits column dot-products from its row-major 3x3 state window. */
void recovered_sharc_opcode_43_project(const uint32_t vector[3],
                                       const uint32_t matrix[9],
                                       uint32_t output[3])
{
    float x = bits_float(vector[0]);
    float y = bits_float(vector[1]);
    float z = bits_float(vector[2]);

    output[0] = float_bits(x * bits_float(matrix[0]) +
                           y * bits_float(matrix[3]) +
                           z * bits_float(matrix[6]));
    output[1] = float_bits(x * bits_float(matrix[1]) +
                           y * bits_float(matrix[4]) +
                           z * bits_float(matrix[7]));
    output[2] = float_bits(x * bits_float(matrix[2]) +
                           y * bits_float(matrix[5]) +
                           z * bits_float(matrix[8]));
}
