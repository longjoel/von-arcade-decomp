/* State-31 range/publication arm recovered from 0x7edc4-0x7ee24. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_range_publication_7edc4_plan {
    u32 related_state_64;
    int16_t related_172;
    u32 scaled_related_172;
    u32 bypasses_range;
    u32 range_passed;
    u32 status_value;
    u32 selector_value;
    u32 action_value;
    u32 control_value;
    u32 continuation_value;
    u32 continuation_target;
    u32 status_destination;
    u32 selector_destination;
    u32 action_destination;
    u32 control_destination;
    u32 continuation_destination;
};

void recovered_state31_range_publication_7edc4(
    u32 related_state_64, int16_t related_172, u32 caller_status,
    struct recovered_state31_range_publication_7edc4_plan *plan)
{
    const u32 scaled = (u32)(int32_t)related_172 << 16;
    const u32 bypass = related_state_64 == 4U;
    const u32 in_range = scaled > 0x150000U && scaled <= 0x190000U;

    plan->related_state_64 = related_state_64;
    plan->related_172 = related_172;
    plan->scaled_related_172 = scaled;
    plan->bypasses_range = bypass;
    plan->range_passed = bypass || in_range;
    plan->status_value = !bypass && !in_range ? 23U : caller_status;
    plan->selector_value = 3U;
    plan->action_value = 20U;
    plan->control_value = 3U;
    plan->continuation_value = 0x64U;
    plan->continuation_target = 0x0007efd8U;
    plan->status_destination = 0x00504d94U;
    plan->selector_destination = 0x00504d98U;
    plan->action_destination = 0x00504db8U;
    plan->control_destination = 0x00504d9cU;
    plan->continuation_destination = 0x00504da0U;
}
