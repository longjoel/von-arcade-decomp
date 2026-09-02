/* Recovered contract for SHARC opcode 0x0a at 0x20211. */
#include <stdint.h>

typedef unsigned int u32;

static float bits_float(u32 bits)
{
    union { u32 bits; float value; } converted = { bits };
    return converted.value;
}

static u32 float_bits(float value)
{
    union { float value; u32 bits; } converted = { value };
    return converted.bits;
}

static float rounded_mul(float left, float right)
{
    volatile float result = left * right;
    return result;
}

extern float recovered_sharc_helper_20d68_candidate(float first, float second);

/*
 * R1 receives the first FIFO word, then the delayed R0 read supplies the
 * helper's other argument before the CALL's delayed branch enters 0x20d68.
 * The helper therefore receives the register pair (R0, R1), not a C-style
 * packet pair.  Keep that distinction explicit: the service result is the
 * helper output * 0x4622f83d (32767/pi), followed by FIX.
 */
u32 recovered_sharc_opcode_0a_angle_registers(u32 r0_bits, u32 r1_bits)
{
    float angle = recovered_sharc_helper_20d68_candidate(bits_float(r0_bits),
                                                         bits_float(r1_bits));
    float scaled = rounded_mul(angle, bits_float(0x4622f83d));
    return (u32)(int32_t)scaled;
}

/* Host packet order is [first FIFO word, second FIFO word]. */
u32 recovered_sharc_opcode_0a_angle(u32 first_bits, u32 second_bits)
{
    return recovered_sharc_opcode_0a_angle_registers(second_bits, first_bits);
}
