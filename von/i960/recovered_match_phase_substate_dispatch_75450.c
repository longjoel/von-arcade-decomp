/* Bounded phase-substate dispatcher and table at i960 0x75450. */

#include <stdint.h>

struct recovered_match_phase_substate_dispatch_75450_plan {
    uint32_t state_register;
    uint32_t state_subtract;
    uint32_t state_lower_bound;
    uint32_t status_source;
    uint32_t status_subtract;
    uint32_t status_lower_bound;
    uint32_t status_upper_bound;
    uint32_t dispatch_table;
    uint32_t dispatch_count;
    uint32_t dispatch_target[14];
    uint32_t reject_target;
    uint32_t local_arm[5];
    uint32_t selected_status[5];
    uint32_t status_destination;
    uint32_t counter_destination;
    uint32_t counter_value;
    uint32_t continuation;
};

void recovered_match_phase_substate_dispatch_75450_plan(
    struct recovered_match_phase_substate_dispatch_75450_plan *plan)
{
    static const uint32_t targets[14] = {
        0x000754acU, 0x000754e4U, 0x000754b4U, 0x000754e4U,
        0x000754e4U, 0x00075cc4U, 0x000754e4U, 0x000754bcU,
        0x000754e4U, 0x000754e4U, 0x000754e4U, 0x000754e4U,
        0x000754c4U, 0x000754ccU
    };
    static const uint32_t arms[5] = {
        0x000754acU, 0x000754b4U, 0x000754bcU,
        0x000754c4U, 0x000754ccU
    };
    static const uint32_t statuses[5] = { 5U, 1U, 8U, 14U, 15U };
    uint32_t index;

    plan->state_register = 4U; /* r4 */
    plan->state_subtract = 3U;
    plan->state_lower_bound = 1U;
    plan->status_source = 0x00504d94U;
    plan->status_subtract = 4U;
    plan->status_lower_bound = 1U;
    plan->status_upper_bound = 13U;
    plan->dispatch_table = 0x00075474U;
    plan->dispatch_count = 14U;
    for (index = 0U; index < plan->dispatch_count; ++index)
        plan->dispatch_target[index] = targets[index];
    plan->reject_target = 0x000754e4U;
    for (index = 0U; index < 5U; ++index) {
        plan->local_arm[index] = arms[index];
        plan->selected_status[index] = statuses[index];
    }
    plan->status_destination = 0x00504d94U;
    plan->counter_destination = 0x00504db8U;
    plan->counter_value = 10U;
    plan->continuation = 0x00075cf0U;
}

uint32_t recovered_match_phase_substate_index(uint32_t status)
{
    return status - 4U;
}
