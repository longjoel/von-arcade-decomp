/* Sibling timing-window route recovered from i960 0x79cc0-0x79d50. */

#include <stdint.h>

enum recovered_transition_timing_window_variant_route_79cc0 {
    RECOVERED_TIMING_VARIANT_ACTION10 = 0,
    RECOVERED_TIMING_VARIANT_ACTION5 = 1,
    RECOVERED_TIMING_VARIANT_SELECTOR_ACTION10 = 2,
    RECOVERED_TIMING_VARIANT_SELECTOR_ACTION5 = 3,
    RECOVERED_TIMING_VARIANT_GATE_TRANSITION = 4
};

struct recovered_transition_timing_window_variant_plan_79cc0 {
    enum recovered_transition_timing_window_variant_route_79cc0 route;
    uint32_t action;
    uint32_t target;
    uint32_t transition;
};

/* lower/upper are the two unresolved converted-threshold outcomes. */
struct recovered_transition_timing_window_variant_plan_79cc0
recovered_transition_timing_window_variant_79cc0(
    uint32_t lower_passed,
    uint32_t upper_passed,
    uint32_t selector,
    uint32_t transition_gate,
    uint32_t object_state)
{
    struct recovered_transition_timing_window_variant_plan_79cc0 plan = {
        RECOVERED_TIMING_VARIANT_ACTION10, 10U, 0x00078408U, 0U
    };

    if (lower_passed != 0U)
        return plan;
    if (upper_passed != 0U) {
        plan.route = RECOVERED_TIMING_VARIANT_ACTION5;
        plan.action = 5U;
        plan.target = 0x000783c8U;
        return plan;
    }
    if (selector < 3U) {
        plan.route = RECOVERED_TIMING_VARIANT_SELECTOR_ACTION10;
        plan.target = 0x00078488U;
        return plan;
    }
    if (selector < 5U) {
        plan.route = RECOVERED_TIMING_VARIANT_SELECTOR_ACTION5;
        plan.action = 5U;
        plan.target = 0x00078448U;
        return plan;
    }
    plan.route = RECOVERED_TIMING_VARIANT_GATE_TRANSITION;
    plan.transition = transition_gate == 1U && object_state == 7U ? 2U : 1U;
    return plan;
}
