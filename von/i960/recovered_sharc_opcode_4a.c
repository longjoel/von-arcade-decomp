/* Recovered normal/early-branch predicate for SHARC opcode 0x4a. */
#include <math.h>
#include <stdint.h>
#include "recovered_float.h"

/* Inputs are (x,y,z,threshold); state[0..3] is the 0x30157 window. */
uint32_t recovered_sharc_opcode_4a_predicate(const uint32_t input[4],
                                             const uint32_t state[5])
{
    float x = recovered_float_from_bits(input[0]) - recovered_float_from_bits(state[0]);
    float y = recovered_float_from_bits(input[1]) - recovered_float_from_bits(state[1]);
    float z = recovered_float_from_bits(input[2]) - recovered_float_from_bits(state[2]);
    if (y > 0.0f)
        return 1U;
    float distance = sqrtf(x * x + y * y + z * z);
    return distance < recovered_float_from_bits(state[3]) + recovered_float_from_bits(input[3]) ? 0U : 1U;
}
