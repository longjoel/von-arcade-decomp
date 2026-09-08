/* Structural model of the geometry-producing follow-up handler at 0x7dc04. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_geometry_handler_7dc04_plan {
    u32 command;
    int32_t negated_field_10;
    int32_t negated_field_8;
    u32 fifo_destination;
    u32 response_low16;
    u32 object_field_184_low16;
    u32 classifier_input;
    u32 result_table;
    u32 result_value;
    u32 counter_destination;
    u32 counter_value;
    u32 selector_destination;
    u32 selector_value;
    u32 status_destination;
};

void recovered_state_followup_geometry_handler_7dc04(
    int32_t object_field_10, int32_t object_field_8, u32 fifo_response,
    u32 object_field_184, u32 classifier_input, u32 result_value,
    u32 caller_g9, struct recovered_state_followup_geometry_handler_7dc04_plan *plan)
{
    plan->command = 10U;
    plan->negated_field_10 = -object_field_10;
    plan->negated_field_8 = -object_field_8;
    plan->fifo_destination = 0x00884000U;
    plan->response_low16 = fifo_response & 0xffffU;
    plan->object_field_184_low16 = object_field_184 & 0xffffU;
    plan->classifier_input = classifier_input;
    plan->result_table = 0x00072b10U;
    plan->result_value = result_value;
    plan->counter_destination = 0x00504db8U;
    plan->counter_value = caller_g9 + 31U;
    plan->selector_destination = 0x00504d98U;
    plan->selector_value = 23U;
    plan->status_destination = 0x00504d94U;
}
