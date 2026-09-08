/* Bounded common update reached by all 0x74e60 state arms. */

#include <stdint.h>

struct recovered_match_transition_common_update_plan {
    uint32_t mode_source;
    uint32_t mode_low_subtract;
    uint32_t mode_low_bound;
    uint32_t mode_high_subtract;
    uint32_t mode_high_bound;
    uint32_t saved_pair_source;
    uint32_t counter_source;
    uint32_t counter_destination;
    uint32_t counter_addend;
    uint32_t zero_selector;
    uint32_t equal_selector;
    uint32_t primary_helper;
    uint32_t floating_source;
    uint32_t floating_zero;
    uint32_t floating_upper_bits;
    uint32_t mode_filter_source;
    uint32_t secondary_helper;
    uint32_t fallback_value;
    uint32_t fallback_destination;
    uint32_t return_address;
};

void recovered_match_transition_common_update_75134_plan(
    struct recovered_match_transition_common_update_plan *plan)
{
    plan->mode_source = 0x00504d80U;
    plan->mode_low_subtract = 13U;
    plan->mode_low_bound = 30U;
    plan->mode_high_subtract = 5U;
    plan->mode_high_bound = 6U;
    plan->saved_pair_source = 0x00504d90U;
    plan->counter_source = 0x00504d8cU;
    plan->counter_destination = 0x00504d8cU;
    plan->counter_addend = 1U;
    plan->zero_selector = 0U;
    plan->equal_selector = 0x00504d90U;
    plan->primary_helper = 0x00082040U;
    plan->floating_source = 0x00504d60U;
    plan->floating_zero = 0U;
    plan->floating_upper_bits = 0x40690000U;
    plan->mode_filter_source = 0x00504d80U;
    plan->secondary_helper = 0x00082650U;
    plan->fallback_value = UINT32_C(0xffffffff);
    plan->fallback_destination = 0x00504d8cU;
    plan->return_address = 0x000751e8U;
}

uint32_t recovered_match_transition_counter_candidate(uint32_t selector,
                                                       uint32_t saved_pair,
                                                       uint32_t current)
{
    return selector == 0U ? current + 1U : saved_pair + 1U;
}

uint32_t recovered_match_transition_fallback_counter(void)
{
    return UINT32_C(0xffffffff);
}
