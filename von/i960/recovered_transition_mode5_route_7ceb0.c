/* Mode-5 transition route recovered from i960 0x7ceb0-0x7cfd8. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_mode5_route_7ceb0_kind {
    RECOVERED_TRANSITION_7CEB0_COORDINATE_ACTION30 = 0,
    RECOVERED_TRANSITION_7CEB0_TIMING_ACTION10 = 1,
    RECOVERED_TRANSITION_7CEB0_TIMING_WRAPPER = 2,
};

struct recovered_transition_mode5_route_7ceb0_plan {
    u32 route;
    u32 coordinate_path;
    u32 selector_source;
    u32 selector_index;
    u32 table_base;
    u32 wrapper_target;
    u32 writes_status;
    u32 status_value;
    u32 writes_transition;
    u32 transition_value;
    u32 writes_action;
    u32 action_value;
};

enum recovered_transition_mode5_selector_source_7ceb0 {
    RECOVERED_TRANSITION_7CEB0_GLOBAL_SELECTOR = 0,
    RECOVERED_TRANSITION_7CEB0_COORDINATE_DIFFERENCE = 1,
};

/*
 * timing_table_arm abstracts the 0x504e0c/0x504d60 comparison: its set arm
 * loads the 0x72840 table and the clear arm calls 0x78408.  selector_index is
 * the already-classified index used by the 0x72780/0x72840 table lookup.
 */
void recovered_transition_mode5_route_7ceb0(
    u32 mode_bits, u32 timing_table_arm, u32 control_504dc8,
    u32 object_state, u32 coordinate_selector, u32 global_selector,
    struct recovered_transition_mode5_route_7ceb0_plan *plan)
{
    plan->route = RECOVERED_TRANSITION_7CEB0_TIMING_WRAPPER;
    plan->coordinate_path = 0U;
    plan->selector_source = RECOVERED_TRANSITION_7CEB0_GLOBAL_SELECTOR;
    plan->selector_index = global_selector;
    plan->table_base = 0U;
    plan->wrapper_target = 0x00078408U;
    plan->writes_status = 0U;
    plan->status_value = 0U;
    plan->writes_transition = 0U;
    plan->transition_value = 0U;
    plan->writes_action = 0U;
    plan->action_value = 0U;

    if ((mode_bits & (1U << 5)) == 0U) {
        plan->route = RECOVERED_TRANSITION_7CEB0_COORDINATE_ACTION30;
        plan->coordinate_path = object_state == 3U ? 1U : 0U;
        plan->selector_source = object_state == 3U
            ? RECOVERED_TRANSITION_7CEB0_COORDINATE_DIFFERENCE
            : RECOVERED_TRANSITION_7CEB0_GLOBAL_SELECTOR;
        plan->selector_index = object_state == 3U
            ? coordinate_selector : global_selector;
        plan->table_base = 0x00072780U;
        plan->writes_status = 1U;
        plan->status_value = 1U;
        plan->writes_action = 1U;
        plan->action_value = 30U;
        return;
    }

    if (timing_table_arm == 0U)
        return;

    plan->route = RECOVERED_TRANSITION_7CEB0_TIMING_ACTION10;
    plan->table_base = 0x00072840U;
    plan->writes_action = 1U;
    plan->action_value = 10U;
    if (control_504dc8 == 1U) {
        plan->writes_transition = 1U;
        plan->transition_value = 2U;
        plan->writes_action = 1U;
        plan->action_value = 25U;
    }
}
