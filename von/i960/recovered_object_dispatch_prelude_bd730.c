/* Deterministic dispatch prelude of i960 0xbd730-0xbd7e8. */
#include "recovered_common.h"

typedef struct {
    uint8_t object_table[32];
    uint16_t record_halfword[32];
    recovered_u32 global_576ba0;
    recovered_u32 global_576ba4;
    recovered_u32 global_576ba8;
} recovered_object_dispatch_state_bd730;

typedef struct {
    recovered_u32 accepted_index[32];
    recovered_u32 dispatch_target[32];
    recovered_u32 context_address[32];
    uint16_t masked_halfword[32];
    recovered_u32 accepted_count;
} recovered_object_dispatch_result_bd730;

/* The indirect callee at 0xbcf40[index * 8] is supplied as a table of
 * addresses.  This function stops at callx, preserving the callee effects
 * and error-reporting path as separate contracts. */
void recovered_object_dispatch_prelude_bd730(
    recovered_object_dispatch_state_bd730 *state,
    const recovered_u32 dispatch_table[256],
    recovered_object_dispatch_result_bd730 *result)
{
    recovered_u32 index;
    state->global_576ba4 = state->global_576ba8;
    result->accepted_count = 0U;
    for (index = 0U; index < 32U; ++index) {
        recovered_u32 value = state->object_table[index];
        if (value > 0xccU)
            continue;
        recovered_u32 accepted = result->accepted_count++;
        result->accepted_index[accepted] = index;
        result->dispatch_target[accepted] = dispatch_table[value];
        result->context_address[accepted] = 0x565320U + index * 0x2cU;
        state->record_halfword[index] =
            (uint16_t)(state->record_halfword[index] & 0xffe0U);
        result->masked_halfword[accepted] = state->record_halfword[index];
    }
    state->global_576ba8 = state->global_576ba4;
}
