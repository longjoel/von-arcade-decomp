/* Recovered normal-case geometry predicate for SHARC opcode 0x47. */
#include <math.h>
#include <stdint.h>

static float bits_float(uint32_t bits)
{
    union { uint32_t bits; float value; } converted = { bits };
    return converted.value;
}

/* Inputs are (a,b,c,d) = (R8,R10,R9,R13); state is the opcode-0x46 window. */
uint32_t recovered_sharc_opcode_47_predicate(const uint32_t input[4],
                                             const uint32_t state[7])
{
    float a = bits_float(input[0]);
    float b = bits_float(input[1]);
    float c = bits_float(input[2]);
    float d = bits_float(input[3]);
    float radial = hypotf(a - bits_float(state[0]),
                          b - bits_float(state[2]));
    float delta = bits_float(state[1]) - d;
    int inside = (c + bits_float(state[5]) > radial &&
                  bits_float(state[4]) <= delta && delta <= bits_float(state[3]));
    return inside ? 0U : 1U;
}
