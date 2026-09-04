/* Recovered row-major matrix projection for SHARC opcode 0x43. */
#include <stdint.h>
#include "recovered_float.h"

/* The ROM emits column dot-products from its row-major 3x3 state window. */
void recovered_sharc_opcode_43_project(const uint32_t vector[3],
                                       const uint32_t matrix[9],
                                       uint32_t output[3])
{
    float x = recovered_float_from_bits(vector[0]);
    float y = recovered_float_from_bits(vector[1]);
    float z = recovered_float_from_bits(vector[2]);

    output[0] = recovered_float_to_bits(x * recovered_float_from_bits(matrix[0]) +
                                        y * recovered_float_from_bits(matrix[3]) +
                                        z * recovered_float_from_bits(matrix[6]));
    output[1] = recovered_float_to_bits(x * recovered_float_from_bits(matrix[1]) +
                                        y * recovered_float_from_bits(matrix[4]) +
                                        z * recovered_float_from_bits(matrix[7]));
    output[2] = recovered_float_to_bits(x * recovered_float_from_bits(matrix[2]) +
                                        y * recovered_float_from_bits(matrix[5]) +
                                        z * recovered_float_from_bits(matrix[8]));
}
