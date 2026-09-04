/* Semantic model of SHARC opcode-0x16 Z-axis row-pair rotation. */

#include <stdint.h>
#include "recovered_float.h"

typedef uint32_t u32;

void recovered_sharc_opcode_16_rotate_z(u32 sine_bits, u32 cosine_bits,
                                         const u32 matrix[9], u32 output[9])
{
    float s = recovered_float_from_bits(sine_bits), c = recovered_float_from_bits(cosine_bits);
    output[6] = matrix[6]; output[7] = matrix[7]; output[8] = matrix[8];
    for (unsigned column = 0; column < 3; ++column) {
        float x = recovered_float_from_bits(matrix[column]);
        float y = recovered_float_from_bits(matrix[3 + column]);
        output[column] = recovered_float_to_bits(c * x - s * y);
        output[3 + column] = recovered_float_to_bits(s * x + c * y);
    }
}
