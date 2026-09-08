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
    int32_t delta;

    if (state_504d7c == 6U && bits_to_float(timing_504d60) < 0.0f) {
        out.value_504d78 = value_504dc8 == 1U ? 3U : 2U;
        return out;
    }

    if (state_504d7c == 3U) {
        delta = 5 - (int32_t)state_504d7c;
        if (1U < (u32)delta) {
            out.value_504d78 = 0U;
            if (value_504dc8 == 1U)
                out.value_504d78 = 3U;
            return out;
        }
    } else if (value_504dc8 == 1U) {
        out.value_504d78 = 3U;
        return out;
    } else if (value_504dcc == 1U) {
        delta = 5 - (int32_t)state_504d7c;
        if (!(1U < (u32)delta))
            out.value_504d78 = 2U;
    }

    delta = 5 - (int32_t)state_504d7c;
    if (out.value_504d78 != 1U && 1U >= (u32)delta) {
        out.value_504d78 = 1U;
        out.state_504d7c = value_504dc0 > 149 ? 6U : 0U;
        out.clear_504d88 = 1U;
    } else {
        out.value_504d78 = 1U;
    }
    if (value_504dc8 == 1U) {
        out.value_504d78 = 3U;
    }
    return out;
}
