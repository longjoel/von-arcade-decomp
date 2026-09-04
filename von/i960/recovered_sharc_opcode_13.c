/* Semantic model of SHARC opcode-0x13 row-scaled 3x3 state writeback. */

typedef unsigned int u32;
#include "recovered_float.h"

void recovered_sharc_opcode_13_scale_rows(const u32 vector[3],
                                          const u32 matrix[9], u32 output[9])
{
    for (unsigned row = 0; row < 3; ++row) {
        float scale = recovered_float_from_bits(vector[row]);
        for (unsigned column = 0; column < 3; ++column) {
            float element = recovered_float_from_bits(matrix[row * 3 + column]);
            output[row * 3 + column] = recovered_float_to_bits(scale * element);
        }
    }
}
