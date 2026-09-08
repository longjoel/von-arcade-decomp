/* Reset tail of the boot stage-record initializer at 0x86810-0x86954. */
#include "recovered_common.h"

typedef struct {
    uint16_t region_5096a0[0x3b0 / 2];
    uint16_t region_509a60[3];
    uint8_t region_509a80[0x40];
    uint8_t region_509ad0[0x40];
    uint8_t latch_509ac0;
    uint8_t latch_509b10;
    recovered_u32 current_words[4];
    recovered_u32 current_pair[2];
    recovered_u32 active_words[4];
    recovered_u32 active_pair[2];
    recovered_u32 previous_words[4];
    recovered_u32 previous_pair[2];
    recovered_u32 stage_guard;
    recovered_u32 epoch_guard;
    recovered_u32 snapshot_epoch;
    recovered_u32 scalar_509a68;
    recovered_u32 scalar_509a6c;
    recovered_u32 scalar_509a70;
} recovered_stage_record_reset_state_86810;

/* Models the stores after the initializer's conditional gate.  The gate at
 * 0x86810 is caller/state dependent; this function begins at its proven clear
 * body, 0x86828, and does not invent the gate predicate. */
void recovered_stage_record_reset_86810(
    recovered_stage_record_reset_state_86810 *state)
{
    recovered_u32 offset;
    for (offset = 0U; offset < 0x3b0U; offset += 16U) {
        state->region_5096a0[offset / 2U] = 0U;
        state->region_5096a0[offset / 2U + 1U] = 0U;
        state->region_5096a0[offset / 2U + 2U] = 0U;
        state->region_5096a0[offset / 2U + 3U] = 0U;
        state->region_5096a0[offset / 2U + 5U] = 0U;
        state->region_5096a0[offset / 2U + 6U] = 0U;
        state->region_5096a0[offset / 2U + 7U] = 0U;
    }
    state->region_509a60[0] = 0U;
    state->region_509a60[1] = 0U;
    state->region_509a60[2] = 0U;
    for (offset = 0U; offset < 0x40U; ++offset) {
        state->region_509a80[offset] = 0U;
        state->region_509ad0[offset] = 0U;
    }
    state->latch_509ac0 = 0U;
    state->latch_509b10 = 0U;
    for (offset = 0U; offset < 4U; ++offset) {
        state->current_words[offset] = 0U;
        state->active_words[offset] = 0U;
        state->previous_words[offset] = 0U;
    }
    state->current_pair[0] = 0U;
    state->current_pair[1] = 0U;
    state->active_pair[0] = 0U;
    state->active_pair[1] = 0U;
    state->previous_pair[0] = 0U;
    state->previous_pair[1] = 0U;
    state->stage_guard = 0U;
    state->epoch_guard = 0U;
    state->snapshot_epoch = 0U;
    state->scalar_509a68 = 0U;
    state->scalar_509a6c = 0U;
    state->scalar_509a70 = 0U;
}
