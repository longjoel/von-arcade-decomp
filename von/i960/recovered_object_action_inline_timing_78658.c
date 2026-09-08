/* Inline object-action timing route reached from 0x78640. */

#include <stdint.h>

struct recovered_object_action_inline_timing_78658_plan {
    uint32_t object_state_offset;
    uint32_t status_dispatcher;
    uint32_t threshold_source;
    uint32_t current_source;
    uint32_t validity_constant;
    uint32_t status_destination;
    uint32_t status_value;
    uint32_t action5_target;
    uint32_t action10_target;
    uint32_t return_address;
};

void recovered_object_action_inline_timing_78658_plan(
    struct recovered_object_action_inline_timing_78658_plan *plan)
{
    plan->object_state_offset = 0x64U;
    plan->status_dispatcher = 0x000784c8U;
    plan->threshold_source = 0x00504dd6U;
    plan->current_source = 0x00504d60U;
    plan->validity_constant = 0x40340000U;
    plan->status_destination = 0x00504d84U;
    plan->status_value = 1U;
    plan->action5_target = 0x000783c8U;
    plan->action10_target = 0x00078408U;
    plan->return_address = 0x000786c0U;
}

uint32_t recovered_object_action_inline_timing_route(uint32_t current,
                                                     uint32_t threshold)
{
    return current >= threshold ? 0x000783c8U : 0x00078408U;
}
