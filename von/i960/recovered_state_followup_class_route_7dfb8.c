/* Classified state route recovered from i960 0x7dfb8-0x7e060. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_class_route_7dfb8_plan {
    u32 enters_class_route;
    u32 continues_to_7e064;
    u32 state_offset;
    u32 global_le_4;
    u32 classifier_input;
    u32 result_table;
    u32 result_index;
    u32 result_value;
    u32 selector_destination;
    u32 selector_value;
    u32 control_destination;
    u32 control_value;
    u32 action_destination;
    u32 action_value;
    u32 call_target;
};

void recovered_state_followup_class_route_7dfb8(
    u32 g6, u32 selector_r6, u32 object_state_64, u32 global_504d70,
    u32 classifier_input, u32 classifier_index, u32 result_value,
    struct recovered_state_followup_class_route_7dfb8_plan *plan)
{
    const u32 class_route = g6 == 0xa3U &&
                            (object_state_64 == 3U || object_state_64 == 6U);

    plan->enters_class_route = class_route ? 1U : 0U;
    plan->continues_to_7e064 = class_route ? 0U : 1U;
    plan->state_offset = object_state_64 == 6U ? 0xfffff800U : 0x00002000U;
    plan->global_le_4 = global_504d70 <= 4U ? 1U : 0U;
    plan->classifier_input = classifier_input;
    plan->result_table = 0U;
    plan->result_index = classifier_index;
    plan->result_value = 0U;
    plan->selector_destination = 0U;
    plan->selector_value = 0U;
    plan->control_destination = 0U;
    plan->control_value = 0U;
    plan->action_destination = 0U;
    plan->action_value = 0U;
    plan->call_target = 0U;

    if (class_route) {
        plan->result_table = 0x00072780U;
        plan->result_value = result_value;
        plan->selector_destination = 0x00504da0U;
        plan->selector_value = selector_r6;
        plan->control_destination = 0x00504d9cU;
        plan->control_value = 1U;
        plan->action_destination = 0x00504db8U;
        plan->action_value = 30U;
        plan->call_target = 0x00079050U;
    }
}
