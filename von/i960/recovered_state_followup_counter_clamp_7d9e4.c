/* Exact publication and counter clamp recovered from i960 0x7d9e4-0x7da10. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_counter_clamp_7d9e4_plan {
    u32 status_value;
    u32 result_value;
    u32 status_destination;
    u32 result_destination;
    u32 counter_before;
    u32 counter_after;
    u32 counter_destination;
};

void recovered_state_followup_counter_clamp_7d9e4(
    u32 selected_status, u32 selected_result, u32 counter_before,
    struct recovered_state_followup_counter_clamp_7d9e4_plan *plan)
{
    u32 counter = counter_before + 1U;
    const int32_t signed_counter = (int32_t)counter;

    if (signed_counter < 0)
        counter = 0U;
    else if (signed_counter > 24)
        counter = 24U;

    plan->status_value = selected_status;
    plan->result_value = selected_result;
    plan->status_destination = 0x00504db8U;
    plan->result_destination = 0x00504d94U;
    plan->counter_before = counter_before;
    plan->counter_after = counter;
    plan->counter_destination = 0x0051c930U;
}
