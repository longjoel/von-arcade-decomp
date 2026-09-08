/* State-8/9 gate recovered from i960 0x7e0d0-0x7e144. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_followup_state89_route_7e0d0 {
    RECOVERED_STATE89_RETURN = 1,
    RECOVERED_STATE89_CALL_81610 = 2,
    RECOVERED_STATE89_CONTINUE_7E144 = 3,
};

struct recovered_state_followup_state89_gate_7e0d0_plan {
    u32 is_state_8_or_9;
    u32 float_gate_passed;
    u32 route;
    u32 target;
};

void recovered_state_followup_state89_gate_7e0d0(
    u32 object_state_64, u32 float_gate_passed,
    struct recovered_state_followup_state89_gate_7e0d0_plan *plan)
{
    plan->is_state_8_or_9 = object_state_64 == 8U || object_state_64 == 9U;
    plan->float_gate_passed = float_gate_passed != 0U ? 1U : 0U;

    if (plan->is_state_8_or_9 == 0U) {
        plan->route = RECOVERED_STATE89_CONTINUE_7E144;
        plan->target = 0x0007e144U;
    } else if (plan->float_gate_passed != 0U) {
        plan->route = RECOVERED_STATE89_CALL_81610;
        plan->target = 0x00081610U;
    } else {
        plan->route = RECOVERED_STATE89_RETURN;
        plan->target = 0x0007e130U;
    }
}
