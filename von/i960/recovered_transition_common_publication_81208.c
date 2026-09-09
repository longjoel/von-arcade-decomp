/* Common publication prefix recovered from i960 0x81208-0x8125c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_common_publication_81208_plan {
    u32 global_table_index;
    u32 result_table;
    u32 result_value;
    u32 control_504dc8;
    float timing_504d60;
    u32 result_destination;
    u32 status_destination;
    u32 published_status;
    u32 status_override;
    u32 target;
};

/* The table result is stored before the control-1 branch. */
void recovered_transition_common_publication_81208(
    u32 global_table_index,
    u32 result_value,
    u32 control_504dc8,
    float timing_504d60,
    struct recovered_transition_common_publication_81208_plan *plan)
{
    const u32 control_one = control_504dc8 == 1U ? 1U : 0U;
    const u32 timing_negative = timing_504d60 < 0.0f ? 1U : 0U;

    plan->global_table_index = global_table_index;
    plan->result_table = 0x000728a0U;
    plan->result_value = result_value;
    plan->control_504dc8 = control_504dc8;
    plan->timing_504d60 = timing_504d60;
    plan->result_destination = 0x00504d94U;
    plan->status_destination = control_one != 0U ? 0x00504d94U : 0U;
    plan->published_status = control_one != 0U ? 23U : 0U;
    plan->status_override = control_one;
    plan->target = control_one == 0U ? 0x000815e0U :
                   timing_negative != 0U ? 0x00081508U : 0x00081518U;
}
