/* Recovered mathematical contract for SHARC opcode 0x3e. */
#include <math.h>
#include <stdint.h>
#include "recovered_float.h"

/*
 * FIFO order is R8, R12, R9, R13, so the service computes the distance
 * between two points represented as (a,c) and (b,d). The ROM's reciprocal
 * refinement can differ from libm by a final representable step.
 */
uint32_t recovered_sharc_opcode_3e_distance(const uint32_t input[4])
{
    float horizontal = recovered_float_from_bits(input[0]) - recovered_float_from_bits(input[1]);
    float vertical = recovered_float_from_bits(input[2]) - recovered_float_from_bits(input[3]);
    /* RSQRTS refinement publishes canonical NaN for zero and unordered
     * radicands rather than a host libm result. */
    if ((horizontal == 0.0f && vertical == 0.0f) ||
        isnan(horizontal) || isnan(vertical))
        return UINT32_C(0xffffffff);
    return recovered_float_to_bits(hypotf(horizontal, vertical));
}
