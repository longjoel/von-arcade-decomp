/* Recovered transition wrapper at i960 0x78c80-0x78d44. */

#include <stdint.h>

struct recovered_transition_state3_variant_state {
    uint32_t transition;
    uint32_t action;
    uint32_t status;
    uint32_t selector_state;
};

/* The state-3/mask-0xc path has priority over the bit-4/gate path. */
void recovered_transition_state3_variant_78c80(
    const uint32_t *transition_table,
    uint32_t selector,
    uint32_t object_state,
    uint32_t mode_bits,
    uint32_t transition_gate,
    struct recovered_transition_state3_variant_state *state)
{
    state->transition = transition_table[selector];
    state->action = 5U;
    state->status = 0U;
    state->selector_state = 0U;

    if (object_state == 3U && (mode_bits & 0xcU) == 0xcU) {
        state->selector_state = 18U;
        state->status = 1U;
        state->action = 20U;
    } else if ((mode_bits & (1U << 4)) != 0U && transition_gate == 1U) {
        state->selector_state = 17U;
        state->status = 1U;
        state->action = 20U;
        if (object_state == 3U && (mode_bits & (1U << 2)) != 0U)
            state->selector_state = 18U;
    }
}
