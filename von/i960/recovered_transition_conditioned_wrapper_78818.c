/* Recovered conditioned transition wrapper at i960 0x78818-0x78880. */

#include <stdint.h>

struct recovered_transition_conditioned_state {
    uint32_t transition;
    uint32_t action;
    uint32_t status;
    uint32_t selector_state;
};

static void recovered_transition_conditioned_wrapper_with_selector(
    const uint32_t *transition_table,
    uint32_t selector,
    uint32_t mode_bits,
    uint32_t transition_gate,
    uint32_t override_selector,
    struct recovered_transition_conditioned_state *state)
{
    state->transition = transition_table[selector];
    state->action = 5U;
    state->status = 0U;
    state->selector_state = 0U;

    if ((mode_bits & (1U << 5)) != 0U && transition_gate == 1U) {
        state->status = 1U;
        state->selector_state = override_selector;
        state->action = 20U;
    }
}

/*
 * The leaf loads the normal transition from 0x72690 and publishes action 5.
 * If bit 5 of 0x504e30 is set and 0x504dc8 equals 1, it additionally writes
 * status 1, selector 6, and replaces the action with 20 before tail-calling
 * the fixed continuation at 0x78880.
 */
void recovered_transition_conditioned_wrapper_78818(
    const uint32_t *transition_table,
    uint32_t selector,
    uint32_t mode_bits,
    uint32_t transition_gate,
    struct recovered_transition_conditioned_state *state)
{
    recovered_transition_conditioned_wrapper_with_selector(
        transition_table, selector, mode_bits, transition_gate, 6U, state);
}

/* 0x78d50 shares the predicate but publishes selector state 18. */
void recovered_transition_conditioned_wrapper_78d50(
    const uint32_t *transition_table,
    uint32_t selector,
    uint32_t mode_bits,
    uint32_t transition_gate,
    struct recovered_transition_conditioned_state *state)
{
    recovered_transition_conditioned_wrapper_with_selector(
        transition_table, selector, mode_bits, transition_gate, 18U, state);
}
