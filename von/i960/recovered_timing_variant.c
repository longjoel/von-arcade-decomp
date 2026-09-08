/* Pure timing split recovered from the object-action arm at i960 0x786d0. */

#include <math.h>
#include <stdint.h>

typedef uint32_t u32;

enum recovered_timing_variant_route {
    RECOVERED_TIMING_VARIANT_REJECT = 0,
    RECOVERED_TIMING_VARIANT_ACTION_5 = 1,
    RECOVERED_TIMING_VARIANT_ACTION_10 = 2,
};

struct recovered_timing_variant_plan {
    enum recovered_timing_variant_route route;
    uint32_t status_write;
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

static u32 recovered_timing_variant_status_write(u32 selector, u32 mode_bits)
{
    switch (selector) {
    case 0U:
    case 6U:
        return (mode_bits & 0x2U) != 0U;
    case 1U:
    case 3U:
        return (mode_bits & 0x4U) != 0U;
    case 2U:
    case 4U:
    case 5U:
    case 7U:
    case 8U:
    case 9U:
        return (mode_bits & 0x6U) != 0U;
    default:
        return 0U;
    }
}

/* 0x786d0 first runs 0x784c8 with object state as the selector. */
struct recovered_timing_variant_plan
recovered_timing_variant_plan(u32 current_bits, u32 threshold_bits,
                              u32 object_state, u32 mode_bits)
{
    struct recovered_timing_variant_plan plan;
    plan.route = recovered_timing_variant_route(current_bits, threshold_bits);
    plan.status_write = recovered_timing_variant_status_write(object_state,
                                                               mode_bits);
    return plan;
}
