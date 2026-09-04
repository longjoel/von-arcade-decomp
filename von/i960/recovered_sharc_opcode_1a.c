/* Semantic model of SHARC opcode-0x1a's affine state-output service. */

typedef unsigned int u32;
#include "recovered_float.h"

/*
 * The SHARC state stores the 3x3 coefficients row-major at offsets 0..8,
 * while the service accumulates one output column at a time: x*m[0,j] +
 * y*m[1,j] + z*m[2,j].  Tail offsets 9..11 are the affine translation.
 */
void recovered_sharc_opcode_1a_affine(const u32 vector[3],
                                      const u32 state[12], u32 output[3])
{
    float x = recovered_float_from_bits(vector[0]);
    float y = recovered_float_from_bits(vector[1]);
    float z = recovered_float_from_bits(vector[2]);

    for (unsigned column = 0; column < 3; ++column) {
        float result = recovered_float_from_bits(state[9 + column]);
        result += x * recovered_float_from_bits(state[column]);
        result += y * recovered_float_from_bits(state[3 + column]);
        result += z * recovered_float_from_bits(state[6 + column]);
        output[column] = recovered_float_to_bits(result);
    }
}
