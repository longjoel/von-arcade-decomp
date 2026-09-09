/* State-2 secondary body recovered from i960 0x812ac-0x81300. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_secondary_state2_812ac_plan {
    u32 control_504dc8;
    u32 flag_504e30;
    u32 result_table;
    u32 result_value;
    u32 result_destination;
    u32 status_destination;
    u32 published_status;
    u32 flag_bit2_set;
    u32 state_destination;
    u32 published_state;
    u32 state_target;
    u32 control_failure_target;
    u32 clear_bit_target;
    u32 target;
};

void recovered_transition_secondary_state2_812ac(
    u32 control_504dc8,
    u32 flag_504e30,
    u32 result_value,
    struct recovered_transition_secondary_state2_812ac_plan *plan)
{
    const u32 control_one = control_504dc8 == 1U ? 1U : 0U;
    const u32 bit2 = (flag_504e30 >> 2U) & 1U;

    plan->control_504dc8 = control_504dc8;
    plan->flag_504e30 = flag_504e30;
    plan->result_table = 0x000728a0U;
    plan->result_value = result_value;
    plan->result_destination = 0x00504d94U;
    plan->status_destination = control_one != 0U ? 0x00504d94U : 0U;
    plan->published_status = control_one != 0U ? 23U : 0U;
    plan->flag_bit2_set = bit2;
    plan->state_destination = control_one != 0U && bit2 != 0U
        ? 0x00504d98U : 0U;
    plan->published_state = control_one != 0U && bit2 != 0U ? 3U : 0U;
    plan->state_target = 0x000815e0U;
    plan->control_failure_target = 0x000815e0U;
    plan->clear_bit_target = 0x0008159cU;
    plan->target = control_one == 0U ? plan->control_failure_target :
                   bit2 == 0U ? plan->clear_bit_target : plan->state_target;
}
