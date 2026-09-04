/* Recovered normal/early-branch predicate for SHARC opcode 0x4c. */
#include <math.h>
#include <stdint.h>
#include "recovered_float.h"

/* Inputs are (x,y,z,bound); state[0..2] is the 0x30157 coordinate origin. */
uint32_t recovered_sharc_opcode_4c_predicate(const uint32_t input[4],
                                             const uint32_t state[5])
{
    float x = recovered_float_from_bits(input[0]) - recovered_float_from_bits(state[0]);
    float y = recovered_float_from_bits(input[1]) - recovered_float_from_bits(state[1]);
    float z = recovered_float_from_bits(input[2]) - recovered_float_from_bits(state[2]);
    if (y < 0.0f)
        return 1U;
    return sqrtf(x * x + y * y + z * z) < recovered_float_from_bits(input[3]) ? 0U : 1U;
}
