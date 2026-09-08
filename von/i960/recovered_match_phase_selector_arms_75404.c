/* Bounded local phase-selector arms reached from 0x753c8. */

#include <stdint.h>

struct recovered_match_phase_selector_arms_75404_plan {
    uint32_t count;
    uint32_t entry[6];
    uint32_t selected_status[6];
    uint32_t status_destination;
    uint32_t counter_destination;
    uint32_t counter_value;
    uint32_t common_status_store;
    uint32_t direct_status_store;
    uint32_t continuation;
};

void recovered_match_phase_selector_arms_75404_plan(
    struct recovered_match_phase_selector_arms_75404_plan *plan)
{
    static const uint32_t entries[6] = {
        0x00075404U, 0x0007540cU, 0x00075414U,
        0x00075424U, 0x0007542cU, 0x00075434U
    };
    static const uint32_t values[6] = { 5U, 4U, 10U, 9U, 16U, 17U };
    uint32_t index;

    plan->count = 6U;
    for (index = 0U; index < plan->count; ++index) {
        plan->entry[index] = entries[index];
        plan->selected_status[index] = values[index];
    }
    plan->status_destination = 0x00504d94U;
    plan->counter_destination = 0x00504db8U;
    plan->counter_value = 10U;
    plan->common_status_store = 0x00075438U;
    plan->direct_status_store = 0x00075418U;
    plan->continuation = 0x00075cf8U;
}

uint32_t recovered_match_phase_selector_counter_value(void)
{
    return 10U;
}
