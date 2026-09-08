/* Special route recovered from i960 0x7df58-0x7dfb4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_special_route_7df58_plan {
    u32 enters_table_route;
    u32 continues_to_7dfb8;
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

void recovered_state_followup_special_route_7df58(
    u32 g6, u32 r6, u32 object_state_64, u32 result_value,
    struct recovered_state_followup_special_route_7df58_plan *plan)
{
    const u32 table_route = (g6 == 0x55U && r6 != 0x56U) ||
                            (g6 == 0xa3U && object_state_64 == 6U);

    plan->enters_table_route = table_route ? 1U : 0U;
    plan->continues_to_7dfb8 = table_route ? 0U : 1U;
    plan->result_table = 0U;
    plan->result_index = 0U;
    plan->result_value = 0U;
    plan->selector_destination = 0U;
    plan->selector_value = 0U;
    plan->control_destination = 0U;
    plan->control_value = 0U;
    plan->action_destination = 0U;
    plan->action_value = 0U;
    plan->call_target = 0U;

    if (table_route) {
        plan->result_table = 0x00072780U;
        plan->result_index = object_state_64;
        plan->result_value = result_value;
        plan->selector_destination = 0x00504da0U;
        plan->selector_value = r6;
        plan->control_destination = 0x00504d9cU;
        plan->control_value = 1U;
        plan->action_destination = 0x00504db8U;
        plan->action_value = 30U;
        plan->call_target = 0x00079050U;
    }
}
