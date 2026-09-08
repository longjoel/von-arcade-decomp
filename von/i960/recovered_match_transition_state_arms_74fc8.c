/* Bounded state arms 6 and 7 plus their shared post-action tail. */

#include <stdint.h>

struct recovered_match_transition_state_arms_67_plan {
    uint32_t arm6_entry;
    uint32_t arm7_entry;
    uint32_t threshold_source;
    uint32_t threshold_99;
    uint32_t threshold_120;
    uint32_t object_state_offset;
    uint32_t mode_source;
    uint32_t boolean_destination;
    uint32_t saved_destination;
    uint32_t state_destination;
    uint32_t transition_destination;
    uint32_t state3;
    uint32_t state6;
    uint32_t low_path_helper;
    uint32_t high_path_helper;
    uint32_t shared_high_path;
    uint32_t shared_post_action;
    uint32_t continuation;
};

void recovered_match_transition_state_arms_74fc8_plan(
    struct recovered_match_transition_state_arms_67_plan *plan)
{
    plan->arm6_entry = 0x00074fc8U;
    plan->arm7_entry = 0x00075048U;
    plan->threshold_source = 0x00504dc0U;
    plan->threshold_99 = 0x63U;
    plan->threshold_120 = 15U << 3;
    plan->object_state_offset = 0x64U;
    plan->mode_source = 0x00504d80U;
    plan->boolean_destination = 0x00504da8U;
    plan->saved_destination = 0x00504d88U;
    plan->state_destination = 0x00504d7cU;
    plan->transition_destination = 0x00504da4U;
    plan->state3 = 3U;
    plan->state6 = 6U;
    plan->low_path_helper = 0x00077e60U;
    plan->high_path_helper = 0x00078090U;
    plan->shared_high_path = 0x0007508cU;
    plan->shared_post_action = 0x000750e0U;
    plan->continuation = 0x00075134U;
}

uint32_t recovered_match_transition_state_threshold(uint32_t value,
                                                    uint32_t threshold)
{
    return value > threshold ? 1U : 0U;
}

uint32_t recovered_match_transition_saved_decrement(uint32_t saved_value)
{
    return saved_value > 1U ? saved_value - 1U : 1U;
}
