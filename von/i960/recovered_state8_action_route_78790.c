/* State-8 action route recovered from i960 0x78790-0x78808. */

#include <math.h>
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state8_action_route_78790 {
    RECOVERED_STATE8_REJECT = 0,
    RECOVERED_STATE8_ACTION5 = 1,
    RECOVERED_STATE8_ACTION10 = 2,
    RECOVERED_STATE8_ACTION10_TABLE_72990 = 3,
    RECOVERED_STATE8_ACTION10_TABLE_729F0 = 4
};

struct recovered_state8_action_plan_78790 {
    enum recovered_state8_action_route_78790 route;
    u32 status_write;
};

static float recovered_state8_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return raw.value;
}

/* threshold_bits represents cvtir(0x504dd6); related_band is 0x504d68. */
struct recovered_state8_action_plan_78790
recovered_state8_action_route_78790(u32 current_bits, u32 threshold_bits,
                                   u32 control_504e28, u32 related_band)
{
    const float current = recovered_state8_float(current_bits);
    const float threshold = recovered_state8_float(threshold_bits);
    const float normalized_delta = fabsf(current - threshold);
    struct recovered_state8_action_plan_78790 plan = {
        RECOVERED_STATE8_REJECT, 0U
    };

    if (!(normalized_delta >= 0.0f)) {
        plan.status_write = 1U;
        return plan;
    }
    if (current <= threshold) {
        plan.route = RECOVERED_STATE8_ACTION10;
        return plan;
    }
    if (control_504e28 != 1U) {
        plan.route = RECOVERED_STATE8_ACTION5;
        return plan;
    }
    plan.route = related_band > 4U
        ? RECOVERED_STATE8_ACTION10_TABLE_729F0
        : RECOVERED_STATE8_ACTION10_TABLE_72990;
    return plan;
}
