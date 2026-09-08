/* Mode-1 transition route recovered from i960 0x7d100-0x7d1ec. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_mode1_route_7d100_kind {
    RECOVERED_TRANSITION_7D100_ENTRY = 0,
    RECOVERED_TRANSITION_7D100_WRAPPER = 1,
    RECOVERED_TRANSITION_7D100_TABLE = 2,
};

struct recovered_transition_mode1_route_7d100_plan {
    u32 route;
    u32 entry_target;
    u32 wrapper_target;
    u32 table_base;
    u32 writes_status;
    u32 status_value;
    u32 writes_transition;
    u32 transition_value;
    u32 writes_action;
    u32 action_value;
};

/*
 * timing_wrapper_arm abstracts the 0x504e0e/0x504d60 comparison.  The
 * wrapper arm reaches 0x78408; its post-call mode/control test is supplied
 * explicitly because the shared global may be changed by that call.
 * table_promotion_eligible abstracts the table arm's selector-bound compare
 * (the 0x7d1b8 subtract/compare sequence).
 */
void recovered_transition_mode1_route_7d100(
    u32 mode_bits, u32 timing_wrapper_arm, u32 control_504dc8,
    u32 post_mode_bits, u32 object_state, u32 table_promotion_eligible,
    struct recovered_transition_mode1_route_7d100_plan *plan)
{
    plan->route = RECOVERED_TRANSITION_7D100_TABLE;
    plan->entry_target = 0x0007a3e0U;
    plan->wrapper_target = 0x00078408U;
    plan->table_base = 0x00072840U;
    plan->writes_status = 0U;
    plan->status_value = 0U;
    plan->writes_transition = 0U;
    plan->transition_value = 0U;
    plan->writes_action = 1U;
    plan->action_value = 10U;

    if ((mode_bits & (1U << 1)) != 0U) {
        plan->route = RECOVERED_TRANSITION_7D100_ENTRY;
        plan->writes_action = 0U;
        plan->action_value = 0U;
        return;
    }

    if (timing_wrapper_arm != 0U) {
        plan->route = RECOVERED_TRANSITION_7D100_WRAPPER;
        plan->table_base = 0U;
        plan->writes_action = 0U;
        plan->action_value = 0U;
        if (control_504dc8 == 1U &&
            (post_mode_bits & (1U << 1)) != 0U) {
            plan->writes_transition = 1U;
            plan->transition_value = 2U;
            plan->writes_action = 1U;
            plan->action_value = 30U;
            if (object_state != 7U) {
                plan->writes_status = 1U;
                plan->status_value = 1U;
            }
        }
        return;
    }

    if (control_504dc8 == 1U || table_promotion_eligible != 0U) {
        plan->writes_transition = 1U;
        plan->transition_value = 2U;
        plan->writes_action = 1U;
        plan->action_value = 30U;
        if (object_state != 7U) {
            plan->writes_status = 1U;
            plan->status_value = 1U;
        }
    }
}
