/* Unsigned-state bypass recovered from i960 0x815ac-0x81604. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_secondary_bypass_815ac_plan {
    u32 current_state_504d68;
    u32 control_504dc8;
    u32 result_table;
    u32 initial_result;
    u32 result_destination;
    u32 control_one;
    u32 final_result;
    u32 status8_value;
    u32 tail_status_destination;
    u32 tail_status;
    u32 tail_selector_destination;
    u32 tail_selector;
    u32 tail_offset_destination;
    u32 tail_offset;
};

void recovered_transition_secondary_bypass_815ac(
    u32 current_state_504d68,
    u32 control_504dc8,
    u32 result_value,
    struct recovered_transition_secondary_bypass_815ac_plan *plan)
{
    const u32 control_one = control_504dc8 == 1U ? 1U : 0U;

    plan->current_state_504d68 = current_state_504d68;
    plan->control_504dc8 = control_504dc8;
    plan->result_table = 0x000728a0U;
    plan->initial_result = result_value;
    plan->result_destination = 0x00504d94U;
    plan->control_one = control_one;
    plan->final_result = control_one != 0U ? 8U : result_value;
    plan->status8_value = 8U;
    plan->tail_status_destination = 0x00504db8U;
    plan->tail_status = 10U;
    plan->tail_selector_destination = 0x00504d9cU;
    plan->tail_selector = 2U;
    plan->tail_offset_destination = 0x00504da0U;
    plan->tail_offset = 0x64U;
}
