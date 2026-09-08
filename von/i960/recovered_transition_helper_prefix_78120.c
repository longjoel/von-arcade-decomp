/* Bounded entry/state-2 prefix of transition helper 0x78120. */

#include <stdint.h>

struct recovered_transition_helper_prefix_78120_plan {
    uint32_t threshold_source;
    uint32_t threshold;
    uint32_t one_time_gate;
    uint32_t linked_object_offset;
    uint32_t input_source;
    uint32_t input_mask;
    uint32_t input_upper_bound;
    uint32_t state_destination;
    uint32_t state_value;
    uint32_t bit_source_register;
    uint32_t low_bit_helper;
    uint32_t high_bit_helper;
    uint32_t bypass_target;
    uint32_t state2_body;
};

void recovered_transition_helper_prefix_78120_plan(
    struct recovered_transition_helper_prefix_78120_plan *plan)
{
    plan->threshold_source = 0x00504dc0U;
    plan->threshold = 0x63U;
    plan->one_time_gate = 0x00504dd0U;
    plan->linked_object_offset = 0x74U;
    plan->input_source = 0x00504d6cU;
    plan->input_mask = 0xffffU;
    plan->input_upper_bound = 0x7ffeU;
    plan->state_destination = 0x00504d7cU;
    plan->state_value = 2U;
    plan->bit_source_register = 5U; /* g5 */
    plan->low_bit_helper = 0x00078448U;
    plan->high_bit_helper = 0x00078488U;
    plan->bypass_target = 0x0007834cU;
    plan->state2_body = 0x00078190U;
}

uint32_t recovered_transition_helper_threshold_pass(uint32_t value)
{
    return value <= 0x63U ? 1U : 0U;
}

uint32_t recovered_transition_helper_mask_input(uint32_t value)
{
    return value & 0xffffU;
}
