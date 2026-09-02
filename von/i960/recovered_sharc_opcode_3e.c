/* Recovered mathematical contract for SHARC opcode 0x3e. */
#include <math.h>
#include <stdint.h>

static float bits_float(uint32_t bits)
{
    union { uint32_t bits; float value; } converted = { bits };
    return converted.value;
}

static uint32_t float_bits(float value)
{
    union { float value; uint32_t bits; } converted = { value };
    return converted.bits;
}

/*
 * FIFO order is R8, R12, R9, R13, so the service computes the distance
 * between two points represented as (a,c) and (b,d). The ROM's reciprocal
 * refinement can differ from libm by a final representable step.
 */
uint32_t recovered_sharc_opcode_3e_distance(const uint32_t input[4])
{
    float horizontal = bits_float(input[0]) - bits_float(input[1]);
    float vertical = bits_float(input[2]) - bits_float(input[3]);
    /* RSQRTS refinement publishes canonical NaN for zero and unordered
     * radicands rather than a host libm result. */
    if ((horizontal == 0.0f && vertical == 0.0f) ||
        isnan(horizontal) || isnan(vertical))
        return UINT32_C(0xffffffff);
    return float_bits(hypotf(horizontal, vertical));
}
