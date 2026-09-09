/* Slot-10 ready-clear entry recovered from i960 0x1aad4-0x1ab40. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_address, status_word, status_threshold;
    recovered_u32 result_r5, result_r6;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 admitted, rejected, zero_phase;
    recovered_u32 progress_helper, progress_helper_call_count;
    recovered_u32 setup_helper, setup_call_count, setup_argument;
    recovered_u32 state_address, state_value, command_address, command_value;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1aad4_ready_clear_entry_result;

int recovered_startup_mode4_arm_1aad4_ready_clear_entry(
    recovered_u32 status_word, recovered_u32 result_r5, recovered_u32 result_r6,
    recovered_u32 phase_value,
    recovered_startup_mode4_arm_1aad4_ready_clear_entry_result *result)
{
    recovered_startup_mode4_arm_1aad4_ready_clear_entry_result r = {0};
    r.status_address = 0x503a18U;
    r.status_word = status_word;
    r.status_threshold = 0xf423eU;
    r.result_r5 = result_r5;
    r.result_r6 = result_r6;
    r.phase_address = 0x503aa0U;
    r.phase_before = phase_value;
    r.phase_after = phase_value + 1U;
    r.progress_helper = 0x1fb50U;
    r.setup_helper = 0x2a4e0U;
    r.setup_argument = 0x1012U;
    r.state_address = 0x503ab0U;
    r.command_address = 0x5032f4U;
    r.continuation = 0x1ab40U;
    if (status_word > r.status_threshold || result_r5 != 0U || result_r6 != 0U) {
        r.rejected = 1U;
        r.continuation = 0x1abecU;
    } else {
        r.admitted = 1U;
        if (phase_value == 0U) {
            r.zero_phase = 1U;
            r.progress_helper_call_count = 1U;
            r.setup_call_count = 1U;
            r.state_value = 5U;
            r.command_value = 0x43U;
            r.continuation = 0x1ac50U;
        }
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
