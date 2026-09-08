/* Recovered transition wrapper at i960 0x000783c8. */

#include <stdint.h>

struct recovered_transition_wrapper_state {
    uint32_t transition;
    uint32_t action;
};

/* The ROM indexes its 0x72690 table with the current 0x504d68 selector. */
void recovered_transition_wrapper(const uint32_t *transition_table,
                                  uint32_t selector,
                                  struct recovered_transition_wrapper_state *state)
{
    state->transition = transition_table[selector];
    state->action = 5U;
}

/* The action-10 sibling at 0x78408 uses the adjacent 0x72750 table. */
void recovered_transition_wrapper_action10(const uint32_t *transition_table,
                                           uint32_t selector,
                                           struct recovered_transition_wrapper_state *state)
{
    state->transition = transition_table[selector];
    state->action = 10U;
}
