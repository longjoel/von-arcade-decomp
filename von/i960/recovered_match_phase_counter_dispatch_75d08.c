/* Bounded phase-counter dispatcher and table at i960 0x75d08. */

#include <stdint.h>

struct recovered_match_phase_counter_dispatch_75d08_plan {
    uint32_t state_register;
    uint32_t state_bound;
    uint32_t status_source;
    uint32_t status_subtract;
    uint32_t status_lower_bound;
    uint32_t status_upper_bound;
    uint32_t dispatch_table;
    uint32_t dispatch_count;
    uint32_t dispatch_target[14];
    uint32_t default_target;
    uint32_t local_arm[5];
    uint32_t selected_status[5];
    uint32_t common_writer;
    uint32_t counter_return;
};

void recovered_match_phase_counter_dispatch_75d08_plan(
    struct recovered_match_phase_counter_dispatch_75d08_plan *plan)
{
    static const uint32_t targets[14] = {
        0x00075d60U, 0x00075d68U, 0x00075d88U, 0x00075d88U,
        0x00075d88U, 0x00075d70U, 0x00075d78U, 0x00075d88U,
        0x00075d88U, 0x00075d88U, 0x00075d88U, 0x00075d88U,
        0x00075d80U, 0x00075cecU
    };
    static const uint32_t arms[5] = {
        0x00075d60U, 0x00075d68U, 0x00075d70U,
        0x00075d78U, 0x00075d80U
    };
    static const uint32_t statuses[5] = { 6U, 1U, 11U, 8U, 14U };
    uint32_t index;

    plan->state_register = 4U; /* r4 */
    plan->state_bound = 6U;
    plan->status_source = 0x00504d94U;
    plan->status_subtract = 4U;
    plan->status_lower_bound = 1U;
    plan->status_upper_bound = 13U;
    plan->dispatch_table = 0x00075d28U;
    plan->dispatch_count = 14U;
    for (index = 0U; index < plan->dispatch_count; ++index)
        plan->dispatch_target[index] = targets[index];
    plan->default_target = 0x00075d88U;
    for (index = 0U; index < 5U; ++index) {
        plan->local_arm[index] = arms[index];
        plan->selected_status[index] = statuses[index];
    }
    plan->common_writer = 0x00075cf0U;
    plan->counter_return = 0x00075cf8U;
}

uint32_t recovered_match_phase_counter_dispatch_index(uint32_t status)
{
    return status - 4U;
}
