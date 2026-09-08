/* Follow-up tail handlers recovered from i960 0x7dc98-0x7dcb8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_tail_handlers_7dc98_plan {
    u32 writes_status;
    u32 status_destination;
    u32 status_value;
    u32 writes_counter;
    u32 counter_destination;
    u32 counter_value;
};

void recovered_state_followup_tail_handler_7dc98(
    u32 target, u32 object_field_170, u32 caller_continuation,
    struct recovered_state_followup_tail_handlers_7dc98_plan *plan)
{
    plan->writes_status = 0U;
    plan->status_destination = 0U;
    plan->status_value = 0U;
    plan->writes_counter = 0U;
    plan->counter_destination = 0U;
    plan->counter_value = 0U;

    if (target == 0x0007dc98U) {
        plan->writes_status = 1U;
        plan->status_destination = 0x00504d94U;
        plan->status_value = 29U;
    } else if (target == 0x0007dca8U && object_field_170 != 6U) {
        plan->writes_counter = 1U;
        plan->counter_destination = 0x0051c930U;
        plan->counter_value = caller_continuation;
    }
}
