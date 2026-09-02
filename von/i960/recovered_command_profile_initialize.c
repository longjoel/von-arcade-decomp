/* Profile initializer recovered from i960 0xc8fa0-0xc9084. */

#include <stdint.h>

typedef uint32_t (*recovered_profile_setup)(uint32_t configuration);
typedef void (*recovered_profile_callback)(uint32_t value);

struct recovered_command_profile_state {
    uint32_t callback_sentinel;
    uint32_t selector;
    uint32_t pending;
    uint32_t profile_long_low;
    uint32_t profile_long_high;
    uint32_t profile_word;
    uint32_t input_handle;
    uint32_t published_handle;
};

/*
 * The callback arguments retain the values visible at each indirect call.
 * setup is the 0x281f0 configuration call, first_handler is c8e10's first
 * table column, and the last two callbacks represent 0x1c618/0x1ccf8.
 */
void recovered_command_profile_initialize(
    uint32_t profile,
    const uint32_t configuration_table[14],
    const uint32_t profile_long_low_table[14],
    const uint32_t profile_long_high_table[14],
    const uint32_t profile_word_table[14],
    const uint32_t profile_format_table[14],
    recovered_profile_setup setup,
    recovered_profile_callback first_handler,
    recovered_profile_callback initialize_helper,
    recovered_profile_callback format_helper,
    struct recovered_command_profile_state *state)
{
    uint32_t handle = 0;

    if (profile != 13U) {
        handle = setup(configuration_table[profile]);
        state->callback_sentinel = UINT32_MAX;
    }

    first_handler(profile);
    state->selector = 0;
    state->pending = 0;
    state->profile_long_low = profile_long_low_table[profile];
    state->profile_long_high = profile_long_high_table[profile];
    state->profile_word = profile_word_table[profile];
    initialize_helper(profile);
    format_helper(profile_format_table[profile]);
    state->input_handle = handle;
    state->published_handle = handle;
}
