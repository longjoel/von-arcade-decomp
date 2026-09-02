/* Profile/handler wrapper recovered from i960 0xc8f10. */

#include <stdint.h>

typedef void (*recovered_command_profile_callback)(uint32_t input);

/*
 * Select the middle handler in the three-column c8e10 table, after running
 * the c5d70 packet preparation callback.  The returned table index is a
 * host-side aid; the ROM's observable result is the two callback effects.
 */
uint32_t recovered_command_profile_dispatch(
    uint16_t control_word,
    uint32_t profile,
    uint32_t input,
    uint32_t *selector_output,
    recovered_command_profile_callback packet_prepare,
    recovered_command_profile_callback handlers[24])
{
    uint32_t table_index = profile * 3U + 1U;

    *selector_output = ((uint32_t)control_word >> 13) & 7U;
    packet_prepare(input);
    handlers[table_index](input);
    return table_index;
}

/* Sibling wrapper at 0xc8f60: third column, then post-call input increment. */
uint32_t recovered_command_profile_advance(
    uint32_t profile,
    uint32_t *input,
    recovered_command_profile_callback handlers[24])
{
    uint32_t table_index = profile * 3U + 2U;
    uint32_t current = *input;

    handlers[table_index](current);
    *input = current + 1U;
    return table_index;
}
