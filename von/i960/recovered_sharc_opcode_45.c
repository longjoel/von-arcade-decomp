/* Recovered normal-case spherical projection for SHARC opcode 0x45. */
#include <math.h>
#include <stdint.h>

static uint32_t float_bits(float value)
{
    union { float value; uint32_t bits; } converted = { value };
    return converted.bits;
}

static float bits_float(uint32_t bits)
{
    union { uint32_t bits; float value; } converted = { bits };
    return converted.value;
}

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

    output[0] = float_bits(scale * sine_a);
    output[1] = float_bits(scale * cosine_a * cosine_b);
    output[2] = float_bits(-scale * cosine_a * sine_b);
}

static float rounded_mul(float left, float right)
{
    volatile float result = left * right;
    return result;
}

static uint32_t fixed_angle_to_radians(int16_t units)
{
    union { uint32_t bits; float value; } scale = { 0x38c9116d };
    volatile float result = (float)units * scale.value;
    return float_bits(result);
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
    float scale = bits_float(scale_bits);
    float sine_a = bits_float(recovered_sharc_helper_20dc4_sine(magnitude_a, negative_a));
    float cosine_a = bits_float(recovered_sharc_helper_20dbe_cosine(magnitude_a, negative_a));
    float sine_b = bits_float(recovered_sharc_helper_20dc4_sine(magnitude_b, negative_b));
    float cosine_b = bits_float(recovered_sharc_helper_20dbe_cosine(magnitude_b, negative_b));

    output[0] = float_bits(rounded_mul(scale, sine_a));
    output[1] = float_bits(rounded_mul(rounded_mul(scale, cosine_a), cosine_b));
    output[2] = float_bits(-rounded_mul(rounded_mul(scale, cosine_a), sine_b));
}
