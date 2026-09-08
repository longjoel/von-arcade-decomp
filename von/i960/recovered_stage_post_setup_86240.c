/* Bounded prefix of the stage post-setup routine at 0x86240-0x86620.
 *
 * The original routine normalizes the threshold words selected by the stage
 * selector, maintains active/previous snapshots, and then initializes the
 * stage working tables.  This file models only the first two contracts.  The
 * mode-specific table payload beginning at 0x86534 remains intentionally
 * outside this model until its destination-field meanings are recovered.
 */
#include "recovered_common.h"

typedef struct {
    recovered_u32 words[4];
    recovered_u32 pair[2];
    recovered_u32 b34;
} recovered_stage_thresholds_86240;

typedef struct {
    recovered_u32 active_words[4];
    recovered_u32 active_pair[2];
    recovered_u32 previous_words[4];
    recovered_u32 previous_pair[2];
    recovered_u32 stage_guard;
    recovered_u32 epoch_guard;
    recovered_u32 snapshot_epoch;
} recovered_stage_snapshot_86240;

static void copy_words(recovered_u32 *dst, const recovered_u32 *src)
{
    recovered_u32 i;
    for (i = 0U; i < 4U; ++i)
        dst[i] = src[i];
}

static void copy_pair(recovered_u32 *dst, const recovered_u32 *src)
{
    dst[0] = src[0];
    dst[1] = src[1];
}

/* Mirrors the two literal families and branch guards at 0x86248-0x86338.
 * The caller supplies the already-selected 0x504dbc timing value. */
void recovered_stage_threshold_normalize_86240(
    recovered_u32 stage, recovered_u32 timing,
    const recovered_stage_thresholds_86240 *input,
    recovered_stage_thresholds_86240 *output)
{
    copy_words(output->words, input->words);
    copy_pair(output->pair, input->pair);
    output->b34 = input->b34;

    /* cmpibl 5,stage followed by cmpible timing,64 selects this family for
     * stages above five or for timings above the 64-unit gate. */
    if (stage > 5U || timing > 64U) {
        if (output->words[0] > 0x9c3U)
            output->words[0] = 0x9c5U;
        if (output->words[1] > 0x5dbU)
            output->words[1] = 0x5ddU;
        if (output->words[2] > 0x4afU)
            output->words[2] = 0x4b1U;
        if (output->words[3] > 0x5dbU)
            output->words[3] = 0x5ddU;
        if (output->pair[0] <= 0x7cfU)
            output->pair[0] = 0x7d1U;
        if (output->pair[1] <= 0x5dbU)
            output->b34 = 0x5ddU;
        return;
    }

    /* The low-timing path first bypasses normalization for stage <= 2 when
     * timing <= stage + 31 (0x862c8-0x86330). */
    if (stage <= 2U && timing <= stage + 31U)
        return;

    if (output->words[0] > 0x2bbU)
        output->words[0] = 0x2bdU;
    if (output->words[1] > 0x1f3U)
        output->words[1] = 0x1f5U;
    if (output->words[2] > 0x1f3U)
        output->words[2] = 0x1f5U;
    if (output->words[3] > 0x1f3U)
        output->words[3] = 0x1f5U;
    if (output->pair[0] > 0x1f3U)
        output->pair[0] = 0x1f5U;
    if (output->pair[1] <= 0x1f3U)
        output->b34 = 0x1f5U;
}

/* Models the snapshot protocol at 0x8633c-0x86434.  A larger stage guard
 * commits the current normalized values to the saved snapshot.  Otherwise a
 * zero transition guard restores that saved snapshot, while a positive
 * transition guard either advances the epoch or restores the active snapshot
 * when the epoch has already been observed. */
void recovered_stage_snapshot_update_86240(
    recovered_u32 stage_guard, recovered_u32 transition_guard,
    recovered_u32 epoch, const recovered_stage_thresholds_86240 *current,
    recovered_stage_thresholds_86240 *effective,
    recovered_stage_snapshot_86240 *state)
{
    *effective = *current;
    if (stage_guard > state->stage_guard) {
        copy_words(state->previous_words, current->words);
        copy_pair(state->previous_pair, current->pair);
        state->snapshot_epoch = 0U;
        state->epoch_guard = 0U;
    } else if (transition_guard == 0U) {
        copy_words(effective->words, state->previous_words);
        copy_pair(effective->pair, state->previous_pair);
        state->snapshot_epoch = 0U;
        state->epoch_guard = 0U;
    } else if (state->epoch_guard < epoch) {
        state->epoch_guard = epoch;
    } else if (state->snapshot_epoch < epoch) {
        copy_words(effective->words, state->active_words);
        copy_pair(effective->pair, state->active_pair);
        state->snapshot_epoch = epoch;
    }

    copy_words(state->active_words, effective->words);
    copy_pair(state->active_pair, effective->pair);
    state->stage_guard = stage_guard;
}

typedef struct {
    uint16_t region_5096a0[0x3b0 / 2];
    uint16_t region_509a60[3];
    uint8_t region_509a80[0x40];
    uint8_t region_509ad0[0x40];
    uint8_t latch_509ac0;
    uint8_t latch_509b10;
    recovered_u32 word_509a68;
    recovered_u32 word_509a6c;
    recovered_u32 word_509a70;
} recovered_stage_clear_state_86240;

/* Exact zero-write schedule at 0x86438-0x86520.  The seven halfword lanes
 * per 16-byte record and the two byte-pair loops are kept explicit because
 * these are stores to a packed runtime layout, not a generic memset. */
void recovered_stage_working_tables_clear_86240(
    recovered_stage_clear_state_86240 *state)
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
    state->word_509a68 = 0U;
    state->word_509a6c = 0U;
    state->word_509a70 = 0U;
}

/* Exact mode presets at 0x86534-0x865e0.  The caller's stage/transition
 * gates are tested before the mode byte: stage zero and nonzero 0x503a74
 * return without publishing a preset.  The returned pair is the value stored
 * at 0x509b70 (and the corresponding current/snapshot publication is left to
 * the caller's global-memory adapter). */
recovered_u32 recovered_stage_mode_seed_86240(
    recovered_u32 stage, recovered_u32 transition, recovered_u32 mode,
    const recovered_stage_thresholds_86240 *input,
    recovered_stage_thresholds_86240 *output)
{
    recovered_u32 value;
    if (stage == 0U || transition != 0U)
        return 0U;

    *output = *input;

    switch (mode) {
    case 1U:
        output->words[0] = 0x2bdU;
        value = 0x1f5U;
        output->words[1] = value;
        output->words[2] = value;
        output->words[3] = value;
        output->pair[0] = value;
        output->pair[1] = value;
        break;
    case 2U:
        output->words[0] = 0x9c5U;
        output->words[1] = 0x5ddU;
        output->words[2] = 0x4b1U;
        output->words[3] = 0x5ddU;
        output->pair[0] = 0x7d1U;
        output->pair[1] = 0x5ddU;
        break;
    case 3U:
        value = 0xfffffd44U;
        output->words[0] = value;
        output->words[1] = value;
        output->words[2] = value;
        output->words[3] = value;
        output->pair[0] = value;
        output->pair[1] = value;
        break;
    default:
        output->words[0] = 0U;
        output->words[1] = 0U;
        output->words[2] = 0U;
        output->words[3] = 0U;
        output->pair[0] = 0U;
        output->pair[1] = 0U;
        break;
    }
    return 1U;
}
