/* Candidate mathematical model of the SHARC helper at 0x20d68.
 *
 * This deliberately models the recovered rational atan approximation, signed
 * quadrant routing, and finite LOGB endpoint guard. It is useful as a readable
 * reference while the exact pipeline schedule and direct-infinity behavior
 * are still being reconstructed.
 */

#include <stdint.h>
#include "recovered_float.h"

typedef unsigned int u32;

static float normalize_sharc_input(float value)
{
    u32 bits = recovered_float_to_bits(value);
    u32 magnitude = bits & 0x7fffffffU;

    /* The SHARC input path canonicalizes NaNs and flushes denormals. */
    if ((magnitude & 0x7f800000U) == 0x7f800000U &&
        (magnitude & 0x007fffffU) != 0U)
        return recovered_float_from_bits(0xffffffffU);
    if ((magnitude & 0x7f800000U) == 0U && magnitude != 0U)
        return recovered_float_from_bits(bits & 0x80000000U);
    return value;
}

static float f32(float value)
{
    volatile float rounded = value;
    return rounded;
}

static float atan_rational(float ratio)
{
    const float c3 = -0.72002685070037841796875f;
    const float c4 = -1.44008350372314453125f;
    const float c5 = 4.7522258758544921875f;
    const float c6 = 4.32025051116943359375f;
    float z = f32(ratio * ratio);
    float numerator = f32(f32(z * c3 + c4) * z);
    float denominator = f32(f32(z + c5) * z + c6);
    return f32(ratio + f32(ratio * f32(numerator / denominator)));
}

static float atan_positive(float ratio)
{
    const float threshold = 0.2679491937160491943359375f;
    const float sqrt_3 = 1.73205077648162841796875f;
    const float pi_over_6 = 0.52359879016876220703125f;
    const float pi_over_2 = 1.57079637050628662109375f;

    if (ratio > 1.0f)
        return f32(pi_over_2 - atan_positive(f32(1.0f / ratio)));
    else if (ratio > threshold)
    {
        /* The delayed branch at 0x20d8b..0x20d96 forms the tangent
         * subtraction identity for pi/6.  The threshold selects whether
         * this reduction is needed; it is not the subtraction constant. */
        float reduced = f32(f32(sqrt_3 * ratio - 1.0f) /
                            f32(sqrt_3 + ratio));
        return f32(pi_over_6 + atan_rational(reduced));
    }
    return atan_rational(ratio);
}

float recovered_sharc_helper_20d68_candidate(float first, float second)
{
    const float pi_over_2 = 1.57079637050628662109375f;
    u32 first_bits;
    u32 second_bits;
    unsigned first_exponent;
    unsigned second_exponent;
    int exponent_distance;
    float ratio;
    float result;

    first = normalize_sharc_input(first);
    second = normalize_sharc_input(second);

    if ((recovered_float_to_bits(first) & 0x7f800000U) == 0x7f800000U &&
        (recovered_float_to_bits(first) & 0x007fffffU) != 0U)
        return recovered_float_from_bits(0xffffffffU);
    if ((recovered_float_to_bits(second) & 0x7f800000U) == 0x7f800000U &&
        (recovered_float_to_bits(second) & 0x007fffffU) != 0U)
        return recovered_float_from_bits(0xffffffffU);

    if (first == 0.0f && second == 0.0f)
        return 0.0f;
    if (second == 0.0f)
        return first < 0.0f ? -1.57079637050628662109375f
                            : 1.57079637050628662109375f;
    if (first == 0.0f)
        return second < 0.0f ? 3.1415927410125732421875f : 0.0f;

    /* The ROM's LOGB comparison exits before RECIPS at a distance of 124.
     * Normal finite values expose the same boundary directly through their
     * exponent fields.  Keep subnormals, infinities, and NaNs outside this
     * readable model until their SHARC-specific LOGB behavior is captured. */
    first_bits = recovered_float_to_bits(first) & 0x7fffffffU;
    second_bits = recovered_float_to_bits(second) & 0x7fffffffU;
    first_exponent = (first_bits >> 23) & 0xffU;
    second_exponent = (second_bits >> 23) & 0xffU;
    if (first_exponent != 0U && first_exponent != 0xffU &&
        second_exponent != 0U && second_exponent != 0xffU)
    {
        exponent_distance = (int)first_exponent - (int)second_exponent;
        if (exponent_distance >= 124)
            return first < 0.0f ? -pi_over_2 : pi_over_2;
        if (exponent_distance <= -124)
            return 0.0f;
    }

    ratio = first / second;
    if (ratio < 0.0f)
        ratio = -ratio;
    result = atan_positive(ratio);

    if (second < 0.0f)
        return first < 0.0f ? f32(result - 3.1415927410125732421875f)
                            : f32(3.1415927410125732421875f - result);
    return first < 0.0f ? -result : result;
}
