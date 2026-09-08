/* Bounded first-arm cluster reached from the 0x74e60 state table. */

#include <stdint.h>

struct recovered_match_transition_state_arm {
    uint32_t entry;
    uint32_t threshold;
    uint32_t state;
    uint32_t boolean_destination;
    uint32_t state_destination;
    uint32_t writes_saved_value;
    uint32_t saved_value_source;
    uint32_t calls_helper;
    uint32_t helper;
    uint32_t continuation;
};

struct recovered_match_transition_state_arms_plan {
    uint32_t count;
    struct recovered_match_transition_state_arm arm[4];
};

void recovered_match_transition_state_arms_plan(
    struct recovered_match_transition_state_arms_plan *plan)
{
    static const uint32_t entries[4] = {
        0x00074ec4U, 0x00074ef0U, 0x00074f28U, 0x00074f3cU
    };
    static const uint32_t thresholds[4] = { 15U << 3, 15U << 3,
                                             15U << 3, 3U << 3 };
    static const uint32_t saved[4] = { 0U, 1U, 0U, 0U };
    uint32_t index;

    plan->count = 4U;
    for (index = 0U; index < plan->count; ++index) {
        plan->arm[index].entry = entries[index];
        plan->arm[index].threshold = thresholds[index];
        plan->arm[index].state = 3U;
        plan->arm[index].boolean_destination = 0x00504da8U;
        plan->arm[index].state_destination = 0x00504d7cU;
        plan->arm[index].writes_saved_value = saved[index];
        plan->arm[index].saved_value_source = saved[index] != 0U ?
            14U : 0U; /* g14, preserved by the caller */
        plan->arm[index].calls_helper = index != 0U ? 1U : 0U;
        plan->arm[index].helper = index != 0U ? 0x00078120U : 0U;
        plan->arm[index].continuation = 0x00075134U;
    }
}

uint32_t recovered_match_transition_arm_boolean(uint32_t value,
                                                uint32_t threshold)
{
    return value > threshold ? 1U : 0U;
}
