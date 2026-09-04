/* Recovered normal-case geometry predicate for SHARC opcode 0x47. */
#include <math.h>
#include <stdint.h>
#include "recovered_float.h"

/* Inputs are (a,b,c,d) = (R8,R10,R9,R13); state is the opcode-0x46 window. */
uint32_t recovered_sharc_opcode_47_predicate(const uint32_t input[4],
                                             const uint32_t state[7])
{
    float a = recovered_float_from_bits(input[0]);
    float b = recovered_float_from_bits(input[1]);
    float c = recovered_float_from_bits(input[2]);
    float d = recovered_float_from_bits(input[3]);
    float radial = hypotf(a - recovered_float_from_bits(state[0]),
                          b - recovered_float_from_bits(state[2]));
    float delta = recovered_float_from_bits(state[1]) - d;
    int inside = (c + recovered_float_from_bits(state[5]) > radial &&
                  recovered_float_from_bits(state[4]) <= delta && delta <= recovered_float_from_bits(state[3]));
    return inside ? 0U : 1U;
}
