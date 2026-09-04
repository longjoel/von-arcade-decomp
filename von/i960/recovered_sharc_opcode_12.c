/* Semantic model of SHARC opcode-0x12 matrix-vector tail accumulation. */

typedef unsigned int u32;
#include "recovered_float.h"

void recovered_sharc_opcode_12_accumulate(const u32 vector[3],
                                          const u32 matrix[9],
                                          const u32 tail[3], u32 output[3])
{
    for (unsigned column = 0; column < 3; ++column) {
        float value = recovered_float_from_bits(tail[column]);
        for (unsigned row = 0; row < 3; ++row)
            value += recovered_float_from_bits(vector[row]) * recovered_float_from_bits(matrix[row * 3 + column]);
        output[column] = recovered_float_to_bits(value);
    }
}
