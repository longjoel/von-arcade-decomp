/* Fallback admission gate recovered from i960 0x7e064-0x7e12c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_fallback_gate_7e064_plan {
    u32 remainder_480;
    u32 enters_81610_route;
    u32 continues_to_7e0d0;
    u32 writes_continuation;
    u32 continuation_destination;
    u32 continuation_value;
    u32 control_destination;
    u32 control_value;
    u32 writes_selector;
    u32 selector_destination;
    u32 selector_value;
    u32 call_target;
};

void recovered_state_followup_fallback_gate_7e064(
    u32 timing_value_5024e8, u32 object_state_64, u32 global_509b34,
    u32 float_gate_passed, u32 g5, u32 g6, u32 control_504dc8,
    u32 caller_continuation,
    struct recovered_state_followup_fallback_gate_7e064_plan *plan)
{
    const u32 remainder = timing_value_5024e8 % 480U;
    const u32 admitted = remainder <= 239U &&
                         object_state_64 != 7U && object_state_64 != 3U &&
                         global_509b34 > 0x1f4U && float_gate_passed != 0U &&
                         g5 != 4U && g6 == 0xa3U;

    plan->remainder_480 = remainder;
    plan->enters_81610_route = admitted ? 1U : 0U;
    plan->continues_to_7e0d0 = admitted ? 0U : 1U;
    plan->writes_continuation = 0U;
    plan->continuation_destination = 0U;
    plan->continuation_value = 0U;
    plan->control_destination = 0U;
    plan->control_value = 0U;
    plan->writes_selector = 0U;
    plan->selector_destination = 0U;
    plan->selector_value = 0U;
    plan->call_target = 0U;

    if (admitted) {
        plan->call_target = 0x00081610U;
        plan->writes_continuation = 1U;
        plan->continuation_destination = 0x00504da0U;
        plan->continuation_value = caller_continuation;
        plan->control_destination = 0x00504d9cU;
        plan->control_value = 1U;
        if (control_504dc8 == 1U) {
            plan->writes_selector = 1U;
            plan->selector_destination = 0x00504d98U;
            plan->selector_value = 1U;
        }
    }
}
