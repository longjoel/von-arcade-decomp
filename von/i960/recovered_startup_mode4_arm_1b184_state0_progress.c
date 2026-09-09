/* Slot-11 state-0/progress arm recovered from i960 0x1b184-0x1b244. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 marker_address, marker_value, marker_match;
    recovered_u32 mode_address, mode_value, mode_target;
    recovered_u32 stored_address, stored_raw, stored_signed, stored_target;
    recovered_u32 stored_updated, stored_update_value, callback_address, callback_value;
    recovered_u32 state_address, state_value;
    recovered_u32 counter_address, counter_before, counter_after;
    recovered_u32 limit_address, limit_value, progress_address, progress_before, progress_after;
    recovered_u32 progress_triggered, trigger_helper, progress_helper;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1b184_state0_progress_result;

int recovered_startup_mode4_arm_1b184_state0_progress(
    recovered_u32 ready_value, recovered_u32 mode_value,
    recovered_u32 stored_raw, recovered_u32 register_r10,
    recovered_u32 counter_value, recovered_u32 limit_value,
    recovered_u32 progress_value, recovered_u32 callback_value,
    recovered_startup_mode4_arm_1b184_state0_progress_result *result)
{
    recovered_startup_mode4_arm_1b184_state0_progress_result r = {0};
    int16_t stored = (int16_t)(stored_raw & 0xffffU);
    recovered_u32 target = register_r10 + 31U;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.marker_address = 0x504134U;
    r.marker_value = mode_value;
    r.marker_match = mode_value == 9U ? 1U : 0U;
    r.mode_address = 0x504134U;
    r.mode_value = mode_value;
    r.mode_target = 9U;
    r.stored_address = 0x504242U;
    r.stored_raw = stored_raw;
    r.stored_signed = (recovered_u32)(int32_t)stored;
    r.stored_target = target;
    r.callback_address = 0x50424aU;
    r.callback_value = callback_value;
    r.state_address = 0x503ab0U;
    r.state_value = 3U;
    r.counter_address = 0x503a6cU;
    r.counter_before = counter_value;
    r.counter_after = counter_value + 1U;
    r.limit_address = 0x503a78U;
    r.limit_value = limit_value;
    r.progress_address = 0x503a94U;
    r.progress_before = progress_value;
    r.progress_after = progress_value;
    r.trigger_helper = 0x20060U;
    r.progress_helper = 0x19b50U;
    r.continuation = 0x1b2fcU;

    if (ready_value == 0U) {
        if (mode_value == 9U && stored == 6) {
            r.stored_updated = 1U;
            r.stored_update_value = 6U;
        } else if (r.stored_signed != target) {
            r.stored_updated = 1U;
            r.stored_update_value = target;
        }
    }
    if (ready_value != 0U &&
        (int32_t)r.counter_after > (int32_t)limit_value) {
        r.progress_triggered = 1U;
        r.progress_after = progress_value + 1U;
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
