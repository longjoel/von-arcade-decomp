/* Pure timing split recovered from the object-action arm at i960 0x786d0. */

#include <math.h>
#include <stdint.h>

typedef uint32_t u32;

enum recovered_timing_variant_route {
    RECOVERED_TIMING_VARIANT_REJECT = 0,
    RECOVERED_TIMING_VARIANT_ACTION_5 = 1,
    RECOVERED_TIMING_VARIANT_ACTION_10 = 2,
};

static float recovered_timing_variant_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return raw.value;
}

/* The action helpers and their mapped-state effects remain outside this leaf. */
enum recovered_timing_variant_route recovered_timing_variant_route(u32 current_bits,
                                                                    u32 threshold_bits)
{
    const float current = recovered_timing_variant_float(current_bits);
    const float threshold = recovered_timing_variant_float(threshold_bits);
    const float normalized_delta = fabsf(current - threshold);

    if (!(normalized_delta >= 0.0f))
        return RECOVERED_TIMING_VARIANT_REJECT;
    return current >= threshold ? RECOVERED_TIMING_VARIANT_ACTION_5
                                 : RECOVERED_TIMING_VARIANT_ACTION_10;
}
