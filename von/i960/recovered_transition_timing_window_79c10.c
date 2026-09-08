/* Timing-window route recovered from i960 0x79c10-0x79cb4. */

#include <stdint.h>

enum recovered_transition_timing_window_route_79c10 {
    RECOVERED_TIMING_WINDOW_ACTION10 = 0,
    RECOVERED_TIMING_WINDOW_ACTION5 = 1,
    RECOVERED_TIMING_WINDOW_OVERRIDE = 2
};

struct recovered_transition_timing_window_plan_79c10 {
    enum recovered_transition_timing_window_route_79c10 route;
    uint32_t status;
    uint32_t selector;
    uint32_t action;
    uint32_t target;
};

/*
 * comparison_path is the already-evaluated result of the two floating
 * threshold comparisons.  This keeps the converted 0x504e04/0x504e06
 * producers outside the pure route model while preserving each assembly exit.
 */
struct recovered_transition_timing_window_plan_79c10
recovered_transition_timing_window_79c10(uint32_t comparison_path,
                                          uint32_t caller_g14)
{
    struct recovered_transition_timing_window_plan_79c10 plan = {
        RECOVERED_TIMING_WINDOW_ACTION10, 0U, 0U, 0U, 0x00078408U
    };

    if (comparison_path == 1U) {
        plan.route = RECOVERED_TIMING_WINDOW_ACTION5;
        plan.target = 0x000783c8U;
        return plan;
    }
    if (comparison_path == 2U) {
        plan.route = RECOVERED_TIMING_WINDOW_OVERRIDE;
        plan.status = 1U;
        plan.selector = caller_g14;
        plan.action = 10U;
        return plan;
    }

    plan.action = 10U;
    return plan;
}
