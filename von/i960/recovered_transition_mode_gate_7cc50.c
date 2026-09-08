/* Mode/timing gate recovered from i960 0x7cc50-0x7ce0c. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_mode_gate_7cc50_route {
    RECOVERED_TRANSITION_7CC50_ENTRY = 0,
    RECOVERED_TRANSITION_7CC50_ACTION30 = 1,
    RECOVERED_TRANSITION_7CC50_ACTION10 = 2,
};

struct recovered_transition_mode_gate_7cc50_plan {
    u32 route;
    u32 entry_target;
    u32 timing_target;
    u32 writes_status;
    u32 status_value;
    u32 writes_transition;
    u32 transition_value;
    u32 writes_action;
    u32 action_value;
    u32 writes_selector;
    u32 selector_value;
};

/*
 * timing_passed abstracts the converted 0x504e0e versus 0x504d60 compare.
 * periodic_passed abstracts the 0x5024e8 remainder check (remainder <= 59).
 * The latter is only examined after both 0x504da4 and 0x504dc8 equal 1.
 */
void recovered_transition_mode_gate_7cc50(
    u32 mode_bits, u32 timing_passed, u32 control_504da4,
    u32 control_504dc8, u32 periodic_passed,
    struct recovered_transition_mode_gate_7cc50_plan *plan)
{
    plan->route = RECOVERED_TRANSITION_7CC50_ACTION10;
    plan->entry_target = 0x0007a3e0U;
    plan->timing_target = 0x00078408U;
    plan->writes_status = 0U;
    plan->status_value = 0U;
    plan->writes_transition = 0U;
    plan->transition_value = 0U;
    plan->writes_action = 0U;
    plan->action_value = 0U;
    plan->writes_selector = 0U;
    plan->selector_value = 0U;

    if ((mode_bits & (1U << 1)) == 0U) {
        plan->route = RECOVERED_TRANSITION_7CC50_ENTRY;
        return;
    }

    if (timing_passed == 0U) {
        plan->route = RECOVERED_TRANSITION_7CC50_ACTION30;
        plan->writes_status = 1U;
        plan->status_value = 1U;
        /* The shared 0x7ce84 tail does not write the transition field; it
         * writes selector 3 below and action 30. */
        plan->writes_action = 1U;
        plan->action_value = 30U;
        plan->writes_selector = 1U;
        plan->selector_value = 3U;
        return;
    }

    if (control_504da4 == 1U && control_504dc8 == 1U &&
        periodic_passed != 0U) {
        plan->writes_selector = 1U;
        plan->selector_value = 3U;
    }
}
