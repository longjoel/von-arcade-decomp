/* Selector-6 publication prefix recovered from i960 0x7fd58-0x7fdd4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_selector6_publication_7fd58_plan {
    u32 global_counter;
    u32 selector_destination;
    u32 selector_value;
    u32 control_destination;
    u32 control_value;
    u32 counter_destination;
    int32_t counter_value;
    u32 counter_limit_passed;
    u32 target;
    u32 deeper_target;
};

void recovered_transition_selector6_publication_7fd58(
    u32 global_counter,
    struct recovered_transition_selector6_publication_7fd58_plan *plan)
{
    const u32 within_limit = global_counter <= 0x9c4U;

    plan->global_counter = global_counter;
    plan->selector_destination = 0x00504d9cU;
    plan->selector_value = 6U;
    plan->control_destination = 0x00504da0U;
    plan->control_value = 0x64U;
    plan->counter_destination = 0x00504db4U;
    plan->counter_value = -1;
    plan->counter_limit_passed = within_limit;
    plan->target = within_limit ? 0x0007fdd4U : 0x0007fd90U;
    plan->deeper_target = 0x0007fd90U;
}
