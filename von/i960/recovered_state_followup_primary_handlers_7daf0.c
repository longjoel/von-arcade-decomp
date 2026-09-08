/* Distinct primary-table follow-up arms recovered from i960 0x7daf0-0x7db6c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_primary_handler_plan {
    u32 writes_selector;
    u32 selector_value;
    u32 writes_status;
    u32 status_value;
    u32 writes_continuation;
    u32 continuation_value;
    u32 decrements_counter;
    u32 counter_destination;
    u32 counter_after;
    u32 selector_destination;
    u32 status_destination;
    u32 continuation_destination;
};

void recovered_state_followup_primary_handler_7daf0(
    u32 target, u32 object_field_172, u32 counter_value,
    u32 caller_continuation,
    struct recovered_state_followup_primary_handler_plan *plan)
{
    plan->writes_selector = 0U;
    plan->selector_value = 0U;
    plan->writes_status = 0U;
    plan->status_value = 0U;
    plan->writes_continuation = 0U;
    plan->continuation_value = 0U;
    plan->decrements_counter = 0U;
    plan->counter_destination = 0U;
    plan->counter_after = 0U;
    plan->selector_destination = 0U;
    plan->status_destination = 0U;
    plan->continuation_destination = 0U;

    if (target == 0x0007daf0U) {
        plan->writes_selector = 1U;
        plan->selector_value = 20U;
        plan->selector_destination = 0x00504d98U;
    } else if (target == 0x0007db00U) {
        plan->writes_selector = 1U;
        plan->selector_value = 23U;
        plan->selector_destination = 0x00504d98U;
        plan->writes_status = 1U;
        plan->status_value = 28U;
        plan->status_destination = 0x00504d94U;
    } else if (target == 0x0007db1cU) {
        plan->writes_selector = 1U;
        plan->selector_value = 21U;
        plan->selector_destination = 0x00504d98U;
    } else if (target == 0x0007db2cU) {
        plan->writes_status = 1U;
        plan->status_value = caller_continuation;
        plan->status_destination = 0x00504d94U;
        if (object_field_172 == 4U) {
            plan->decrements_counter = 1U;
            plan->counter_destination = 0x0051c930U;
            plan->counter_after = counter_value - 1U;
        }
    } else if (target == 0x0007db54U) {
        plan->writes_status = 1U;
        plan->status_value = caller_continuation;
        plan->status_destination = 0x00504d94U;
        if (object_field_172 != 6U) {
            plan->writes_continuation = 1U;
            plan->continuation_value = caller_continuation;
            plan->continuation_destination = 0x0051c930U;
        }
    }
}
