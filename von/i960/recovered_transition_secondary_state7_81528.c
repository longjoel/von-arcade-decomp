/* State-7 secondary body recovered from i960 0x81528-0x815ac. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_secondary_state7_81528_plan {
    u32 control_504dc8;
    u32 object_state_64;
    u32 flag_504e30;
    u32 current_state_504d68;
    u32 result_table;
    u32 result_value;
    u32 result_destination;
    u32 initial_status;
    u32 final_state_destination;
    u32 published_state;
    u32 object_state3_match;
    u32 flag_bit2_set;
    u32 flag_bit1_set;
    u32 control_failure_target;
    u32 state3_target;
    u32 state2_target;
    u32 state1_target;
    u32 target;
};

void recovered_transition_secondary_state7_81528(
    u32 control_504dc8,
    u32 object_state_64,
    u32 flag_504e30,
    u32 current_state_504d68,
    u32 result_value,
    struct recovered_transition_secondary_state7_81528_plan *plan)
{
    const u32 control_one = control_504dc8 == 1U ? 1U : 0U;
    const u32 object_state3 = object_state_64 == 3U ? 1U : 0U;
    const u32 bit2 = (flag_504e30 >> 2U) & 1U;
    const u32 bit1 = (flag_504e30 >> 1U) & 1U;
    const u32 state3 = object_state3 != 0U || bit2 != 0U ? 1U : 0U;
    const u32 state2 = state3 == 0U && bit1 != 0U ? 1U : 0U;

    plan->control_504dc8 = control_504dc8;
    plan->object_state_64 = object_state_64;
    plan->flag_504e30 = flag_504e30;
    plan->current_state_504d68 = current_state_504d68;
    plan->result_table = 0x000728a0U;
    plan->result_value = result_value;
    plan->result_destination = 0x00504d94U;
    plan->initial_status = control_one != 0U ? 9U : 0U;
    plan->final_state_destination = control_one != 0U ? 0x00504d98U : 0U;
    plan->published_state = control_one == 0U ? 0U :
                            state3 != 0U ? 3U :
                            state2 != 0U ? 2U : 1U;
    plan->object_state3_match = object_state3;
    plan->flag_bit2_set = bit2;
    plan->flag_bit1_set = bit1;
    plan->control_failure_target = 0x000815e0U;
    plan->state3_target = 0x000815e0U;
    plan->state2_target = 0x000815e0U;
    plan->state1_target = 0x000815e0U;
    plan->target = plan->control_failure_target;
}
