/* Transition route recovered from i960 0x80710-0x807cc. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_route_80710 {
    RECOVERED_TRANSITION_ROUTE_80710_REJECT = 0,
    RECOVERED_TRANSITION_ROUTE_80710_CLASSIFY = 1
};

struct recovered_transition_route_plan_80710 {
    enum recovered_transition_route_80710 route;
    u32 band_index;
    int32_t adjusted_current;
    int32_t raw_difference;
    u32 status_504db8;
    u32 threshold_call_82800;
};

static u32 signed_band(int32_t raw)
{
    const int16_t value = (int16_t)(uint32_t)raw;
    if (value >= 0)
        return value <= 0x038d ? 0U : value <= 0x1554 ? 1U :
               value <= 0x3fff ? 2U : value <= 0x5fff ? 3U : 4U;
    return value < -0x6000 ? 5U : value < -0x4000 ? 6U :
           value < -0x1555 ? 7U : value < -0x038e ? 8U : 9U;
}

/* current_184 and related_184 are the sign-extended halfwords before the
 * observed 16-bit normalization; threshold/current are host float values. */
struct recovered_transition_route_plan_80710
recovered_transition_route_80710(
    int32_t global_504d70, int16_t current_184, int16_t related_184,
    float threshold_504df8, float current_timing)
{
    struct recovered_transition_route_plan_80710 out = {
        RECOVERED_TRANSITION_ROUTE_80710_REJECT, 0U, 0, 0, 10U, 0U
    };
    int32_t adjusted;

    if (global_504d70 <= 1) {
        adjusted = (int32_t)current_184 - 0x6800;
    } else if (global_504d70 <= 9) {
        adjusted = (int32_t)current_184 + 0x6800;
    } else {
        return out;
    }
    out.route = RECOVERED_TRANSITION_ROUTE_80710_CLASSIFY;
    out.adjusted_current = adjusted;
    out.raw_difference = (int32_t)related_184 - adjusted;
    out.band_index = signed_band(out.raw_difference);
    out.threshold_call_82800 = current_timing < threshold_504df8;
    return out;
}
