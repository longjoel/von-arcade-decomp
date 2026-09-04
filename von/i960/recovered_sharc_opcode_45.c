/* Recovered normal-case spherical projection for SHARC opcode 0x45. */
#include <math.h>
#include <stdint.h>
#include "recovered_float.h"

/*
 * The first two inputs arrive as signed-16 half-turn units. The fixed-point
 * helpers implement radians ~= word*pi/32767; callers pass that converted
 * angle here so the remaining spherical projection is explicit. The ROM's
 * helper rounding is not replaced by a claim of bit-identical libm output.
 */
void recovered_sharc_opcode_45_project(float angle_a, float angle_b,
                                       float scale, uint32_t output[3])
{
    float sine_a = sinf(angle_a);
    float cosine_a = cosf(angle_a);
    float sine_b = sinf(angle_b);
    float cosine_b = cosf(angle_b);

    output[0] = recovered_float_to_bits(scale * sine_a);
    output[1] = recovered_float_to_bits(scale * cosine_a * cosine_b);
    output[2] = recovered_float_to_bits(-scale * cosine_a * sine_b);
}

static uint32_t fixed_angle_to_radians(int16_t units)
{
    union { uint32_t bits; float value; } scale = { 0x38c9116d };
    volatile float result = (float)units * scale.value;
    return recovered_float_to_bits(result);
}

/* Recovered ROM reduction entry points used by the opcode-0x45 caller. */
extern uint32_t recovered_sharc_helper_20dc4_sine(uint32_t magnitude, int negative);
extern uint32_t recovered_sharc_helper_20dbe_cosine(uint32_t magnitude, int negative);

/* Bit-exact normal-path model for the signed-16 caller used by opcode 0x45. */
void recovered_sharc_opcode_45_project_fixed(int16_t angle_a, int16_t angle_b,
                                              uint32_t scale_bits, uint32_t output[3])
{
    int negative_a = angle_a < 0;
    int negative_b = angle_b < 0;
    uint32_t magnitude_a = fixed_angle_to_radians(negative_a ? -angle_a : angle_a);
    uint32_t magnitude_b = fixed_angle_to_radians(negative_b ? -angle_b : angle_b);
    float scale = recovered_float_from_bits(scale_bits);
    float sine_a = recovered_float_from_bits(recovered_sharc_helper_20dc4_sine(magnitude_a, negative_a));
    float cosine_a = recovered_float_from_bits(recovered_sharc_helper_20dbe_cosine(magnitude_a, negative_a));
    float sine_b = recovered_float_from_bits(recovered_sharc_helper_20dc4_sine(magnitude_b, negative_b));
    float cosine_b = recovered_float_from_bits(recovered_sharc_helper_20dbe_cosine(magnitude_b, negative_b));

    output[0] = recovered_float_to_bits(recovered_rounded_mul(scale, sine_a));
    output[1] = recovered_float_to_bits(recovered_rounded_mul(recovered_rounded_mul(scale, cosine_a), cosine_b));
    output[2] = recovered_float_to_bits(-recovered_rounded_mul(recovered_rounded_mul(scale, cosine_a), sine_b));
}
