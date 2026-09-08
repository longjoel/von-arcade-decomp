/* Mode-5 dispatch recovered from i960 0x7cfe0-0x7d068. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_mode5_dispatch_7cfe0_route {
    RECOVERED_TRANSITION_7CFE0_TIMING_WRAPPER = 0,
    RECOVERED_TRANSITION_7CFE0_TIMING_ACTION10 = 1,
    RECOVERED_TRANSITION_7CFE0_SECONDARY_DISPATCH = 2,
};

struct recovered_transition_mode5_dispatch_7cfe0_plan {
    u32 route;
    u32 wrapper_target;
    u32 secondary_target;
    u32 table_base;
    u32 writes_status;
    u32 status_value;
    u32 writes_transition;
    u32 transition_value;
    u32 writes_action;
    u32 action_value;
};

/*
 * timing_table_arm abstracts the 0x504e0c/0x504d60 comparison.  With mode
 * bit 5 clear, its clear arm calls 0x78408 and its table arm loads 0x72840.
 * Mode bit 5 set bypasses that comparison and calls 0x79d60 directly.
 */
void recovered_transition_mode5_dispatch_7cfe0(
    u32 mode_bits, u32 timing_table_arm, u32 control_504dc8,
    struct recovered_transition_mode5_dispatch_7cfe0_plan *plan)
{
    plan->route = RECOVERED_TRANSITION_7CFE0_TIMING_WRAPPER;
    plan->wrapper_target = 0x00078408U;
    plan->secondary_target = 0x00079d60U;
    plan->table_base = 0U;
    plan->writes_status = 0U;
    plan->status_value = 0U;
    plan->writes_transition = 0U;
    plan->transition_value = 0U;
    plan->writes_action = 0U;
    plan->action_value = 0U;

    if ((mode_bits & (1U << 5)) != 0U) {
        plan->route = RECOVERED_TRANSITION_7CFE0_SECONDARY_DISPATCH;
        plan->writes_status = 1U;
        plan->status_value = 1U;
        return;
    }

    if (timing_table_arm == 0U)
        return;

    plan->route = RECOVERED_TRANSITION_7CFE0_TIMING_ACTION10;
    plan->table_base = 0x00072840U;
    plan->writes_action = 1U;
    plan->action_value = 10U;
    if (control_504dc8 == 1U) {
        plan->writes_transition = 1U;
        plan->transition_value = 2U;
        plan->action_value = 25U;
    }
}
