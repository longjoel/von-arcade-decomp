/* Result/status selector recovered from i960 0x7d9b4-0x7d9e0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_result_select_7d9b4_plan {
    u32 result_table;
    u32 result_index;
    u32 result_value;
    u32 status_value;
    u32 used_class_table;
    u32 used_threshold_table;
    u32 used_literal_fallback;
};

void recovered_state_followup_result_select_7d9b4(
    u32 caller_g9, u32 range_class,
    u32 sample_above_0x40518000, u32 pointer_table_value,
    u32 threshold_table_value,
    struct recovered_state_followup_result_select_7d9b4_plan *plan)
{
    plan->result_table = 0U;
    plan->result_index = 0U;
    plan->result_value = 0U;
    plan->status_value = 0U;
    plan->used_class_table = 0U;
    plan->used_threshold_table = 0U;
    plan->used_literal_fallback = 0U;

    if (range_class != 0U) {
        plan->result_table = 0x00072ab0U;
        plan->result_value = pointer_table_value;
        plan->status_value = caller_g9 + 31U;
        plan->result_index = range_class;
        plan->used_class_table = 1U;
    } else if (sample_above_0x40518000 != 0U) {
        plan->result_table = 0x00072630U;
        plan->result_value = threshold_table_value;
        plan->status_value = caller_g9 + 31U;
        plan->used_threshold_table = 1U;
    } else {
        plan->status_value = 20U;
        plan->used_literal_fallback = 1U;
    }
}
