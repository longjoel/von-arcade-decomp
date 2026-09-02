/* Bounded model of the shared SHARC 0x20dca sine/reduction body. */
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

/* Force the same single-precision boundary as a SHARC RND32 operation. */
static float rounded_mul(float left, float right)
{
    volatile float result = left * right;
    return result;
}

static float rounded_add(float left, float right)
{
    volatile float result = left + right;
    return result;
}

static float rounded_sub(float left, float right)
{
    volatile float result = left - right;
    return result;
}

/*
 * The ROM keeps pi as a high word plus a correction word.  Reconstructing
 * their sum in long double preserves the correction that would disappear if
 * both words were immediately converted to an ordinary float.
 */
static long double recovered_pi(void)
{
    return (long double)bits_float(0x40491000) +
           (long double)bits_float(0xb715777a);
}

static float evaluate_polynomial(float residual)
{
    static const uint32_t coefficient_bits[] = {
        0xab4f7739, /* c4 */
        0x2f3072ab, /* c5 */
        0xb2d731a6, /* c6 */
        0x3638ef1c, /* c7 */
        0xb9500d01, /* c8 */
        0x3c088889, /* c9 */
        0xbe2aaaab, /* c10 */
    };
    float squared = rounded_mul(residual, residual);
    float polynomial = bits_float(coefficient_bits[0]);

    for (unsigned index = 1; index < sizeof(coefficient_bits) / sizeof(coefficient_bits[0]); ++index)
        polynomial = rounded_add(rounded_mul(squared, polynomial), bits_float(coefficient_bits[index]));

    return rounded_add(rounded_mul(rounded_mul(squared, polynomial), residual), residual);
}

static float evaluate_sine(float x, int negative)
{
    long double pi = recovered_pi();
    int quadrant = (int)((long double)x / pi);
    float residual = (float)((long double)x - (long double)quadrant * pi);
    float result = evaluate_polynomial(residual);
    if ((quadrant & 1) != 0)
        result = -result;
    if (negative)
        result = -result;
    return result;
}

/*
 * Evaluate the visible c4..c10 Horner chain after the fixed-point staging.
 * The caller supplies the magnitude in F8 and the original sign in
 * `negative`; this covers the normal 0..pi endpoint contract currently
 * established by the runtime traces.  Wider quadrant/caller state remains
 * intentionally outside this bounded model.
 */
uint32_t recovered_sharc_helper_20dc4_sine(uint32_t magnitude, int negative)
{
    return float_bits(evaluate_sine(bits_float(magnitude), negative));
}

/* 0x20dbe seeds the same body with pi/2, producing the ROM's cos path. */
uint32_t recovered_sharc_helper_20dbe_cosine(uint32_t magnitude, int negative)
{
    float angle = bits_float(magnitude);
    /* 0x20dbe starts with ABS(F0); the observed cosine service is even. */
    (void)negative;
    /* The ROM uses +pi/2 before the shared reducer.  Subtraction is an
     * equivalent mathematical identity, but not an equivalent finite
     * polynomial and therefore loses the observed low bits. */
    float phase = rounded_add(bits_float(0x3fc90fdb), angle);
    int quadrant = (int)rounded_mul(phase, bits_float(0x3ea2f983));
    float phase_fraction = (float)quadrant - 0.5f;
    float residual = rounded_sub(
        rounded_sub(angle, rounded_mul(bits_float(0x40491000), phase_fraction)),
        rounded_mul(bits_float(0xb715777a), phase_fraction));
    return float_bits(evaluate_polynomial(residual) * ((quadrant & 1) ? -1.0f : 1.0f));
}
