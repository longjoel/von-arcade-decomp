/* Bounded late phase selector at i960 0x75c58. */

#include <stdint.h>

struct recovered_match_phase_late_selector_75c58_plan {
    uint32_t state_register;
    uint32_t state_subtract;
    uint32_t state_lower_bound;
    uint32_t status_source;
    uint32_t status_subtract;
    uint32_t status_upper_bound;
    uint32_t dispatch_table;
    uint32_t dispatch_count;
    uint32_t dispatch_target[14];
    uint32_t default_target;
    uint32_t local_arm[5];
    uint32_t selected_status[5];
    uint32_t next_dispatch;
    uint32_t common_writer;
};

void recovered_match_phase_late_selector_75c58_plan(
    struct recovered_match_phase_late_selector_75c58_plan *plan)
{
    static const uint32_t targets[14] = {
        0x00075cb4U, 0x00075d04U, 0x00075cbcU, 0x00075d04U,
        0x00075d04U, 0x00075cc4U, 0x00075d04U, 0x00075cdcU,
        0x00075d04U, 0x00075d04U, 0x00075d04U, 0x00075d04U,
        0x00075ce4U, 0x00075cecU
    };
    static const uint32_t arms[5] = {
        0x00075cb4U, 0x00075cbcU, 0x00075cc4U,
        0x00075cdcU, 0x00075ce4U
    };
    static const uint32_t statuses[5] = { 5U, 1U, 10U, 8U, 14U };
    uint32_t index;

    plan->state_register = 4U; /* r4 */
    plan->state_subtract = 5U;
    plan->state_lower_bound = 1U;
    plan->status_source = 0x00504d94U;
    plan->status_subtract = 4U;
    plan->status_upper_bound = 13U;
    plan->dispatch_table = 0x00075c7cU;
    plan->dispatch_count = 14U;
    for (index = 0U; index < plan->dispatch_count; ++index)
        plan->dispatch_target[index] = targets[index];
    plan->default_target = 0x00075d04U;
    for (index = 0U; index < 5U; ++index) {
        plan->local_arm[index] = arms[index];
        plan->selected_status[index] = statuses[index];
    }
    plan->next_dispatch = 0x00075d08U;
    plan->common_writer = 0x00075cf0U;
}

uint32_t recovered_match_phase_late_selector_index(uint32_t status)
{
    return status - 4U;
}
