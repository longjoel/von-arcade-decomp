/* Dual timing-window transition route recovered from i960 0x79910-0x79a8c. */

#include <stdint.h>

enum recovered_transition_dual_window_route_79910 {
    RECOVERED_DUAL_WINDOW_INNER_OVERRIDE = 0,
    RECOVERED_DUAL_WINDOW_ACTION10 = 1,
    RECOVERED_DUAL_WINDOW_ACTION5 = 2,
    RECOVERED_DUAL_WINDOW_TABLE = 3
};

struct recovered_transition_dual_window_plan_79910 {
    enum recovered_transition_dual_window_route_79910 route;
    uint32_t status;
    uint32_t selector;
    uint32_t transition;
    uint32_t action;
    uint32_t target;
};

/* window_path abstracts the unresolved 0x504e0e/0x504e10 comparisons. */
struct recovered_transition_dual_window_plan_79910
recovered_transition_dual_window_79910(
    uint32_t window_path,
    uint32_t caller_state,
    uint32_t object_state,
    uint32_t transition_gate,
    uint32_t related_selector,
    uint32_t table_transition,
    uint32_t caller_g14)
{
    struct recovered_transition_dual_window_plan_79910 plan = {
        RECOVERED_DUAL_WINDOW_TABLE, 0U, table_transition, 0U, 10U, 0U
    };

    if (window_path == 1U) {
        plan.route = RECOVERED_DUAL_WINDOW_ACTION10;
        plan.action = 10U;
        plan.target = 0x00078408U;
    } else if (window_path == 2U) {
        plan.route = RECOVERED_DUAL_WINDOW_ACTION5;
        plan.action = 5U;
        plan.target = 0x000783c8U;
    } else if (window_path == 3U && transition_gate == 1U) {
        plan.route = RECOVERED_DUAL_WINDOW_INNER_OVERRIDE;
        plan.status = 1U;
        plan.selector = caller_g14;
        plan.transition = 3U;
        plan.action = 20U;
    }

    if (window_path == 0U && (caller_state == 0U || caller_state == 9U)) {
        plan.status = 1U;
        plan.transition = 3U;
        plan.action = 20U;
    }

    if (object_state == 8U &&
        (transition_gate == 1U || related_selector < 7U)) {
        plan.status = 1U;
        plan.transition = 3U;
        plan.action = 20U;
    } else if (object_state == 9U &&
               (transition_gate == 1U || related_selector < 6U)) {
        plan.status = 1U;
        plan.transition = 3U;
        plan.action = 20U;
    }
    return plan;
}
