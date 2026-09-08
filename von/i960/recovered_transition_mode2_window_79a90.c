/* Mode-2 dual timing-window route recovered from i960 0x79a90-0x79c04. */

#include <stdint.h>

enum recovered_transition_mode2_window_route_79a90 {
    RECOVERED_MODE2_WINDOW_ACTION10 = 0,
    RECOVERED_MODE2_WINDOW_ACTION5 = 1,
    RECOVERED_MODE2_WINDOW_TABLE = 2,
    RECOVERED_MODE2_WINDOW_INNER_OVERRIDE = 3
};

struct recovered_transition_mode2_window_plan_79a90 {
    enum recovered_transition_mode2_window_route_79a90 route;
    uint32_t initial_status;
    uint32_t status;
    uint32_t selector;
    uint32_t transition;
    uint32_t action;
    uint32_t target;
};

/* window_path abstracts the two converted-threshold comparisons. */
struct recovered_transition_mode2_window_plan_79a90
recovered_transition_mode2_window_79a90(
    uint32_t window_path,
    uint32_t mode_word,
    uint32_t object_state,
    uint32_t transition_gate,
    uint32_t related_selector,
    uint32_t table_transition,
    uint32_t caller_g14)
{
    struct recovered_transition_mode2_window_plan_79a90 plan = {
        RECOVERED_MODE2_WINDOW_TABLE, mode_word == 1U ? 1U : 0U, 0U,
        table_transition, 0U, 10U, 0U
    };

    if (window_path == 1U) {
        plan.route = RECOVERED_MODE2_WINDOW_ACTION10;
        plan.action = 10U;
        plan.target = 0x00078408U;
    } else if (window_path == 2U) {
        plan.route = RECOVERED_MODE2_WINDOW_ACTION5;
        plan.action = 5U;
        plan.target = 0x000783c8U;
    } else if (window_path == 3U &&
               (mode_word & 0x4U) != 0U && transition_gate == 1U) {
        plan.route = RECOVERED_MODE2_WINDOW_INNER_OVERRIDE;
        plan.status = 1U;
        plan.selector = caller_g14;
        plan.transition = 3U;
        plan.action = 20U;
    } else if (window_path == 0U && (mode_word == 0U || mode_word == 9U)) {
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
