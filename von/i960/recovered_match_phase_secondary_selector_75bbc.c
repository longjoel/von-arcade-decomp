/* Bounded parallel phase selector at i960 0x75bbc. */

#include <stdint.h>

struct recovered_match_phase_secondary_selector_75bbc_plan {
    uint32_t state_register;
    uint32_t state_subtract;
    uint32_t state_lower_bound;
    uint32_t status_source;
    uint32_t status_subtract;
    uint32_t status_upper_bound;
    uint32_t dispatch_table;
    uint32_t dispatch_count;
    uint32_t dispatch_target[15];
    uint32_t default_target;
    uint32_t local_arm[5];
    uint32_t selected_status[5];
    uint32_t common_writer;
    uint32_t next_selector;
};

void recovered_match_phase_secondary_selector_75bbc_plan(
    struct recovered_match_phase_secondary_selector_75bbc_plan *plan)
{
    static const uint32_t targets[15] = {
        0x00075c1cU, 0x00075c54U, 0x00075c54U, 0x00075c54U,
        0x00075c54U, 0x00075c24U, 0x00075c54U, 0x00075cc4U,
        0x00075c54U, 0x00075c54U, 0x00075c2cU, 0x00075c54U,
        0x00075c54U, 0x00075c34U, 0x00075c3cU
    };
    static const uint32_t arms[5] = {
        0x00075c1cU, 0x00075c24U, 0x00075c2cU,
        0x00075c34U, 0x00075c3cU
    };
    static const uint32_t statuses[5] = { 5U, 4U, 9U, 16U, 17U };
    uint32_t index;

    plan->state_register = 4U; /* r4 */
    plan->state_subtract = 3U;
    plan->state_lower_bound = 1U;
    plan->status_source = 0x00504d94U;
    plan->status_subtract = 1U;
    plan->status_upper_bound = 14U;
    plan->dispatch_table = 0x00075be0U;
    plan->dispatch_count = 15U;
    for (index = 0U; index < plan->dispatch_count; ++index)
        plan->dispatch_target[index] = targets[index];
    plan->default_target = 0x00075c54U;
    for (index = 0U; index < 5U; ++index) {
        plan->local_arm[index] = arms[index];
        plan->selected_status[index] = statuses[index];
    }
    plan->common_writer = 0x00075cf0U;
    plan->next_selector = 0x00075c58U;
}

uint32_t recovered_match_phase_secondary_selector_index(uint32_t status)
{
    return status - 1U;
}
