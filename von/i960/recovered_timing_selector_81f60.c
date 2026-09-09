/* Timing/state selector recovered from i960 0x81f60-0x82034. */

#include <stdint.h>

typedef uint32_t u32;

static float bits_to_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return raw.value;
}

struct recovered_timing_selector_81f60 {
    u32 value_504d78;
    u32 state_504d7c;
    u32 clear_504d88;
};

struct recovered_timing_selector_81f60
recovered_timing_selector_81f60(u32 initial_value, u32 timing_504d60,
                                u32 state_504d7c, u32 value_504dc8,
                                u32 value_504dcc, int32_t value_504dc0)
{
    struct recovered_timing_selector_81f60 out = {
        initial_value, state_504d7c, 0U
    };
    const float fast_threshold = bits_to_float(0x404e0000U);

    if (state_504d7c == 6U && bits_to_float(timing_504d60) < fast_threshold) {
        out.value_504d78 = value_504dc8 == 1U ? 3U : 2U;
        return out;
    }

    if (state_504d7c == 3U) {
        if (value_504dc8 == 1U) {
            out.value_504d78 = 3U;
            out.state_504d7c = 4U;
            return out;
        }
        if (value_504dcc == 1U) {
            out.value_504d78 = 0U;
            return out;
        }
    } else if (state_504d7c <= 2U || state_504d7c >= 6U) {
        out.value_504d78 = 0U;
        if (value_504dc8 == 1U)
            out.value_504d78 = 3U;
        return out;
    } else if (value_504dc8 == 1U) {
        out.value_504d78 = 3U;
        return out;
    } else if (value_504dcc == 1U && state_504d7c >= 4U &&
               state_504d7c <= 5U) {
        out.value_504d78 = 2U;
        return out;
    }

    if (out.value_504d78 == 1U) {
        return out;
    }
    if (state_504d7c >= 3U && state_504d7c <= 5U) {
        out.value_504d78 = 1U;
        out.state_504d7c = value_504dc0 > 149 ? 6U : 0U;
        out.clear_504d88 = 1U;
    } else {
        out.value_504d78 = 1U;
    }
    return out;
}
