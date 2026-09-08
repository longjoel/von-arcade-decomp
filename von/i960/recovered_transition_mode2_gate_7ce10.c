/* Mode-2/timing gate recovered from i960 0x7ce10-0x7ceac. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_mode2_gate_7ce10_route {
    RECOVERED_TRANSITION_7CE10_ENTRY = 0,
    RECOVERED_TRANSITION_7CE10_ACTION30_TAIL = 1,
    RECOVERED_TRANSITION_7CE10_ACTION10 = 2,
};

struct recovered_transition_mode2_gate_7ce10_plan {
    u32 route;
    u32 entry_target;
    u32 timing_target;
    u32 writes_status;
    u32 status_value;
    u32 writes_selector;
    u32 selector_value;
    u32 writes_action;
    u32 action_value;
};

/*
 * timing_passed abstracts the converted 0x504e0e versus 0x504d60 compare.
 * periodic_passed abstracts the 0x5024e8 remainder <= 59 check.  A clear
 * timing result enters the shared 0x7ce84 tail, which is intentionally
 * represented as a separate route because it does not write a transition.
 */
void recovered_transition_mode2_gate_7ce10(
    u32 mode_bits, u32 timing_passed, u32 control_504da4,
    u32 control_504dc8, u32 periodic_passed,
    struct recovered_transition_mode2_gate_7ce10_plan *plan)
{
    plan->route = RECOVERED_TRANSITION_7CE10_ACTION10;
    plan->entry_target = 0x0007a3e0U;
    plan->timing_target = 0x00078408U;
    plan->writes_status = 0U;
    plan->status_value = 0U;
    plan->writes_selector = 0U;
    plan->selector_value = 0U;
    plan->writes_action = 0U;
    plan->action_value = 0U;

    if ((mode_bits & (1U << 2)) == 0U) {
        plan->route = RECOVERED_TRANSITION_7CE10_ENTRY;
        return;
    }

    if (timing_passed == 0U) {
        plan->route = RECOVERED_TRANSITION_7CE10_ACTION30_TAIL;
        plan->writes_status = 1U;
        plan->status_value = 1U;
        plan->writes_selector = 1U;
        plan->selector_value = 3U;
        plan->writes_action = 1U;
        plan->action_value = 30U;
        return;
    }

    if (control_504da4 == 1U && control_504dc8 == 1U &&
        periodic_passed != 0U) {
        plan->writes_selector = 1U;
        plan->selector_value = 3U;
    }
}
