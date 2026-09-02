/* Recovered normal/early-branch predicate for SHARC opcode 0x4c. */
#include <math.h>
#include <stdint.h>

static float bits_float(uint32_t bits)
{
    union { uint32_t bits; float value; } converted = { bits };
    return converted.value;
}

/* Inputs are (x,y,z,bound); state[0..2] is the 0x30157 coordinate origin. */
uint32_t recovered_sharc_opcode_4c_predicate(const uint32_t input[4],
                                             const uint32_t state[5])
{
    float x = bits_float(input[0]) - bits_float(state[0]);
    float y = bits_float(input[1]) - bits_float(state[1]);
    float z = bits_float(input[2]) - bits_float(state[2]);
    if (y < 0.0f)
        return 1U;
    return sqrtf(x * x + y * y + z * z) < bits_float(input[3]) ? 0U : 1U;
}
