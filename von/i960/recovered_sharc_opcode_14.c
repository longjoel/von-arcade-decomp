/* Semantic model of SHARC opcode-0x14 X-axis row-pair rotation. */

#include <stdint.h>
#include "recovered_float.h"

typedef uint32_t u32;

void recovered_sharc_opcode_14_rotate_x(u32 sine_bits, u32 cosine_bits,
                                         const u32 matrix[9], u32 output[9])
{
    float sine = recovered_float_from_bits(sine_bits);
    float cosine = recovered_float_from_bits(cosine_bits);

    output[0] = matrix[0];
    output[1] = matrix[1];
    output[2] = matrix[2];
    for (unsigned column = 0; column < 3; ++column) {
        float row1 = recovered_float_from_bits(matrix[3 + column]);
        float row2 = recovered_float_from_bits(matrix[6 + column]);
        output[3 + column] = recovered_float_to_bits(cosine * row1 - sine * row2);
        output[6 + column] = recovered_float_to_bits(sine * row1 + cosine * row2);
    }
}
