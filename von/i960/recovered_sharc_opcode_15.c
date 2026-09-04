/* Semantic model of SHARC opcode-0x15 Y-axis row-pair rotation. */

#include <stdint.h>
#include "recovered_float.h"

typedef uint32_t u32;

void recovered_sharc_opcode_15_rotate_y(u32 sine_bits, u32 cosine_bits,
                                         const u32 matrix[9], u32 output[9])
{
    float s = recovered_float_from_bits(sine_bits), c = recovered_float_from_bits(cosine_bits);
    output[3] = matrix[3]; output[4] = matrix[4]; output[5] = matrix[5];
    for (unsigned row = 0; row < 3; ++row) {
        float x = recovered_float_from_bits(matrix[row]);
        float z = recovered_float_from_bits(matrix[6 + row]);
        output[row] = recovered_float_to_bits(c * x + s * z);
        output[6 + row] = recovered_float_to_bits(-s * x + c * z);
    }
}
