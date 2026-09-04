/* Exact byte/state transition recovered from the original i960 slice at 0x3a38. */
#include <stdint.h>

struct recovered_input_byte_parser_3a38_state {
    uint8_t first;
    uint8_t second;
    uint16_t count;
    uint32_t status_mask;
};

/*
 * Apply one invocation of the parser.  The return value identifies the
 * listing branch: 0 is the empty no-op, 1 is the signed-underflow first-byte
 * path, 2 is the zero-first-byte path, 3 is the positive-first-byte path,
 * and 4 is the replenishment path for a nonzero count.
 */
uint32_t recovered_input_byte_parser_3a38(
    struct recovered_input_byte_parser_3a38_state *state, uint32_t bit)
{
    uint8_t old_first = state->first;

    if (old_first == 0U && state->second == 0U) {
        if (state->count == 0U)
            return 0U;
        state->count = (uint16_t)(state->count - 1U);
        state->first = 7U;
        state->second = 7U;
        if (bit < 32U)
            state->status_mask |= (uint32_t)1U << bit;
        return 4U;
    }

    state->first = (uint8_t)(old_first - 1U);
    if (old_first == 0U)
        return 1U;
    if (old_first == 1U) {
        if (bit < 32U)
            state->status_mask &= ~((uint32_t)1U << bit);
        return 2U;
    }

    state->second = (uint8_t)(state->second - 1U);
    return 3U;
}
