/* Timing/status sibling recovered from i960 0x78740-0x78780. */

#include <math.h>
#include <stdint.h>

typedef uint32_t u32;

struct recovered_timing_status_variant_78740 {
    u32 action10;
    u32 status_write;
    u32 dispatcher_status_write;
    u32 valid;
    u32 threshold_source;
    u32 current_source;
    u32 status_destination;
    u32 action10_target;
};

static u32 recovered_timing_status_dispatch_write_784c8(u32 selector,
                                                        u32 mode_bits)
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

static float recovered_timing_status_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return raw.value;
}

/*
 * The entry first passes object +0x64 through the shared 0x784c8 status
 * dispatcher. The normalized absolute-difference guard then rejects unordered values. For
 * comparable values, the original arm calls 0x78408 only when current is
 * strictly greater than the converted 0x504dd8 threshold; the <= arm writes
 * status 1 and returns without selecting an action helper.
 */
struct recovered_timing_status_variant_78740
recovered_timing_status_variant_78740(u32 current_bits, u32 threshold_bits,
                                      u32 object_state, u32 mode_bits)
{
    const float current = recovered_timing_status_float(current_bits);
    const float threshold = recovered_timing_status_float(threshold_bits);
    const float normalized_delta = fabsf(current - threshold);
    struct recovered_timing_status_variant_78740 result = {
        0U, 0U, recovered_timing_status_dispatch_write_784c8(object_state,
                                                              mode_bits), 0U,
        0x00504dd8U, 0x00504d60U,
        0x00504d84U, 0x00078408U
    };

    if (!(normalized_delta >= 0.0f))
        return result;
    result.valid = 1U;
    if (current > threshold)
        result.action10 = 1U;
    else
        result.status_write = 1U;
    return result;
}
