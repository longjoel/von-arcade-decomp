/* Shared phase-substate publication reached by the 0x754ac arms. */

#include <stdint.h>

struct recovered_match_phase_substate_common_update_75cf0_plan {
    uint32_t selected_value_register;
    uint32_t selected_value_destination;
    uint32_t counter_value;
    uint32_t counter_destination;
    uint32_t return_address;
};

void recovered_match_phase_substate_common_update_75cf0_plan(
    struct recovered_match_phase_substate_common_update_75cf0_plan *plan)
{
    plan->selected_value_register = 2U; /* g2 */
    plan->selected_value_destination = 0x00504d94U;
    plan->counter_value = 10U;
    plan->counter_destination = 0x00504db8U;
    plan->return_address = 0x00075d04U;
}

uint32_t recovered_match_phase_substate_common_counter(void)
{
    return 10U;
}
