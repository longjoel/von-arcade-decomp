/* Recovered normal-case 3D distance predicate for SHARC opcode 0x49. */
#include <math.h>
#include <stdint.h>

static float bits_float(uint32_t bits)
{
    union { uint32_t bits; float value; } converted = { bits };
    return converted.value;
}

/* Inputs are (x,y,z,threshold); state[0..3] is the 0x30157 window. */
uint32_t recovered_sharc_opcode_49_predicate(const uint32_t input[4],
                                             const uint32_t state[5])
{
    float x = bits_float(input[0]) - bits_float(state[0]);
    float y = bits_float(input[1]) - bits_float(state[1]);
    float z = bits_float(input[2]) - bits_float(state[2]);
    float threshold = bits_float(input[3]);
    float distance = sqrtf(x * x + y * y + z * z);
    return distance < bits_float(state[3]) + threshold ? 0U : 1U;
}
