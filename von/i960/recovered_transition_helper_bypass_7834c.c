/* Deterministic bypass tail reached by transition helper 0x78120. */

#include <stdint.h>

struct recovered_transition_helper_bypass_7834c_plan {
    uint32_t selector_source;
    uint32_t state_destination;
    uint32_t state_value;
    uint32_t selector_threshold;
    uint32_t low_status;
    uint32_t high_status;
    uint32_t status_destination;
    uint32_t counter_value;
    uint32_t counter_destination;
    uint32_t return_address;
};

void recovered_transition_helper_bypass_7834c_plan(
    struct recovered_transition_helper_bypass_7834c_plan *plan)
{
    plan->selector_source = 0x00504d68U;
    plan->state_destination = 0x00504d7cU;
    plan->state_value = 3U;
    plan->selector_threshold = 4U;
    plan->low_status = 12U;
    plan->high_status = 13U;
    plan->status_destination = 0x00504d94U;
    plan->counter_value = 5U;
    plan->counter_destination = 0x00504db8U;
    plan->return_address = 0x00078384U;
}

uint32_t recovered_transition_helper_bypass_status(uint32_t selector)
{
    return selector > 4U ? 13U : 12U;
}
