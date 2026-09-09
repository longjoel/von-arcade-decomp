/* Slot-11 state-1/state-5 latch arm recovered from i960 0x1b244-0x1b2cc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode_address, mode_value, mode_target;
    recovered_u32 latch_address, latch_raw, latch_signed;
    recovered_u32 latch_shifted, latch_sentinel;
    recovered_u32 register_r10, target_value;
    recovered_u32 latch_updated, latch_update_value;
    recovered_u32 callback_address, callback_value;
    recovered_u32 state_address, state_value;
    recovered_u32 counter_address, counter_before, counter_after;
    recovered_u32 callback_save_address, callback_save_value;
    recovered_u32 helper_call, continuation;
} recovered_startup_mode4_arm_1b244_state45_latch_result;

int recovered_startup_mode4_arm_1b244_state45_latch(
    recovered_u32 mode_value, recovered_u32 latch_raw, recovered_u32 register_r10,
    recovered_u32 counter_value, recovered_u32 callback_value,
    recovered_startup_mode4_arm_1b244_state45_latch_result *result)
{
    recovered_startup_mode4_arm_1b244_state45_latch_result r = {0};
    int16_t latch = (int16_t)(latch_raw & 0xffffU);
    recovered_u32 target = register_r10 + 31U;
    r.mode_address = 0x503b34U;
    r.mode_value = mode_value;
    r.mode_target = 9U;
    r.latch_address = 0x503c42U;
    r.latch_raw = latch_raw;
    r.latch_signed = (recovered_u32)(int32_t)latch;
    r.latch_shifted = r.latch_signed << 16U;
    r.latch_sentinel = 0x290000U;
    r.register_r10 = register_r10;
    r.target_value = target;
    r.callback_address = 0x503c4aU;
    r.callback_value = callback_value;
    r.state_address = 0x503ab0U;
    r.state_value = 4U;
    r.counter_address = 0x503a70U;
    r.counter_before = counter_value;
    r.counter_after = counter_value + 1U;
    r.callback_save_address = 0x504b94U;
    r.callback_save_value = callback_value;
    r.helper_call = 0x20180U;
    r.continuation = 0x1b2fcU;

    if (mode_value == 9U && latch == 6) {
        r.latch_updated = 1U;
        r.latch_update_value = 6U;
    } else if (r.latch_shifted != r.latch_sentinel) {
        r.latch_updated = 1U;
        r.latch_update_value = target;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
