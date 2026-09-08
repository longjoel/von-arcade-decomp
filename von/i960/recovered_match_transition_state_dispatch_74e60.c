/* Bounded state-dispatch prefix recovered from i960 0x74e60. */

#include <stdint.h>

struct recovered_match_transition_state_dispatch_plan {
    uint32_t threshold_source;
    uint32_t threshold;
    uint32_t boolean_destination;
    uint32_t selector_source;
    uint32_t selector_limit;
    uint32_t dispatch_table;
    uint32_t dispatch_count;
    uint32_t dispatch_target[8];
    uint32_t first_arm_threshold;
    uint32_t first_arm_state;
    uint32_t first_arm_destination;
};

void recovered_match_transition_state_dispatch_plan(
    struct recovered_match_transition_state_dispatch_plan *plan)
{
    static const uint32_t targets[8] = {
        0x00074ec4U, 0x00074ef0U, 0x00074f28U, 0x00074f3cU,
        0x00074f60U, 0x00074fa0U, 0x00074fc8U, 0x00075048U
    };
    uint32_t index;

    plan->threshold_source = 0x00504dc0U;
    plan->threshold = 0x96U;
    plan->boolean_destination = 0x00504da4U;
    plan->selector_source = 0x00504d7cU;
    plan->selector_limit = 7U;
    plan->dispatch_table = 0x00074ea4U;
    plan->dispatch_count = 8U;
    for (index = 0U; index < plan->dispatch_count; ++index)
        plan->dispatch_target[index] = targets[index];
    plan->first_arm_threshold = 15U << 3;
    plan->first_arm_state = 3U;
    plan->first_arm_destination = 0x00504da8U;
}

uint32_t recovered_match_transition_threshold_flag(uint32_t value)
{
    return value > 0x96U ? 1U : 0U;
}
