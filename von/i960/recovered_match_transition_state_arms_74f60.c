/* Bounded state arms 4 and 5 reached from the 0x74e60 dispatch table. */

#include <stdint.h>

struct recovered_match_transition_state_arm45_plan {
    uint32_t arm4_entry;
    uint32_t arm4_saved_source;
    uint32_t arm4_boolean_destination;
    uint32_t arm4_zero_saved_target;
    uint32_t arm4_nonzero_state;
    uint32_t arm4_nonzero_state_destination;
    uint32_t arm4_nonzero_helper;
    uint32_t arm4_saved_destination;
    uint32_t arm5_entry;
    uint32_t arm5_boolean_destination;
    uint32_t arm5_state;
    uint32_t arm5_state_destination;
    uint32_t arm5_helper;
    uint32_t arm5_saved_source;
    uint32_t arm5_saved_destination;
    uint32_t continuation;
};

void recovered_match_transition_state_arms_74f60_plan(
    struct recovered_match_transition_state_arm45_plan *plan)
{
    plan->arm4_entry = 0x00074f60U;
    plan->arm4_saved_source = 0x00504d88U;
    plan->arm4_boolean_destination = 0x00504da8U;
    plan->arm4_zero_saved_target = 0x00078090U;
    plan->arm4_nonzero_state = 5U;
    plan->arm4_nonzero_state_destination = 0x00504d7cU;
    plan->arm4_nonzero_helper = 0x00077e60U;
    plan->arm4_saved_destination = 0x00504d88U;
    plan->arm5_entry = 0x00074fa0U;
    plan->arm5_boolean_destination = 0x00504da8U;
    plan->arm5_state = 6U;
    plan->arm5_state_destination = 0x00504d7cU;
    plan->arm5_helper = 0x00077e60U;
    plan->arm5_saved_source = 14U; /* g14 */
    plan->arm5_saved_destination = 0x00504d88U;
    plan->continuation = 0x00075134U;
}

uint32_t recovered_match_transition_arm4_zero_saved(uint32_t saved_value)
{
    return saved_value == 0U ? 1U : 0U;
}
