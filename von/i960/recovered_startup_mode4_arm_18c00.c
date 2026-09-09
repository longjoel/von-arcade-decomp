/* First phase-table arm recovered from i960 0x18c00-0x18d9c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_address, state_before, state_after;
    recovered_u32 initialization_call, initialization_argument, initialization_performed;
    recovered_u32 reset_call, progress_call, progress_call_count;
    recovered_u32 device_word_address, device_word;
    recovered_u32 check_mask, checks_required, checks_passed, check_offsets[7];
    recovered_u32 special_device_word, special_device_exception;
    recovered_u32 success_path, success_progress_address, success_progress_value;
    recovered_u32 record_state_call, record_state_first, record_state_second;
    recovered_u32 formatter_call[3], formatter_call_count;
    recovered_u32 ready_address, ready_after;
    recovered_u32 command_address, command_value;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 phase_incremented, fallback_path;
    recovered_u32 cleanup_address, cleanup_value, return_target;
} recovered_startup_mode4_arm_result_18c00;

int recovered_startup_mode4_arm_18c00(
    recovered_u32 state_value, recovered_u32 device_word, recovered_u32 hardware_mode,
    recovered_u32 check_mask, recovered_u32 phase_value,
    recovered_startup_mode4_arm_result_18c00 *result)
{
    recovered_startup_mode4_arm_result_18c00 r = {0};
    static const recovered_u32 offsets[7] = {
        0xffedU, 0xff9eU, 0xff90U, 0xff70U, 0xff60U, 0xffb0U, 0xff02U
    };
    r.state_address = 0x504c98U;
    r.state_before = state_value;
    r.state_after = state_value;
    r.initialization_call = 0x2a870U;
    r.initialization_argument = 1U;
    r.initialization_performed = state_value == 0U ? 1U : 0U;
    r.reset_call = 0x31a8U;
    r.progress_call = 0x503a88U;
    r.progress_call_count = r.initialization_performed;
    r.device_word_address = 0x5024f4U;
    r.device_word = device_word;
    r.check_mask = check_mask;
    r.special_device_word = 0x52U;
    r.special_device_exception = device_word == r.special_device_word ? 1U : 0U;
    r.checks_required = r.special_device_exception != 0U ? 6U : 7U;
    r.checks_passed = 0U;
    for (recovered_u32 i = 0; i < 7U; ++i) {
        r.check_offsets[i] = offsets[i];
        if ((check_mask & (1U << i)) != 0U &&
            (i < 6U || r.special_device_exception == 0U))
            ++r.checks_passed;
    }
    r.success_path = (device_word != 16U &&
                      r.checks_passed == r.checks_required) ? 1U : 0U;
    r.success_progress_address = 0x503a04U;
    r.success_progress_value = 0x293U;
    r.record_state_call = 0x1cac8U;
    r.record_state_first = 28U;
    r.record_state_second = 29U;
    r.formatter_call[0] = 0x1ebb0U;
    r.formatter_call[1] = 0x1ec20U;
    r.formatter_call[2] = 0x1ecb0U;
    r.formatter_call_count = r.success_path != 0U ? 3U : 0U;
    r.ready_address = 0x503a7cU;
    r.ready_after = r.success_path != 0U ? 1U : 0U;
    r.command_address = 0x5032f4U;
    r.command_value = 35U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_incremented = r.success_path != 0U ? 1U : 0U;
    r.fallback_path = (r.success_path == 0U && device_word != 0xffffU &&
                       hardware_mode != 0U && state_value < 4U) ? 1U : 0U;
    if (r.success_path != 0U) {
        r.phase_after = phase_value + 1U;
    } else if (r.fallback_path != 0U) {
        r.phase_after = 3U;
    } else {
        r.phase_after = phase_value;
        r.state_after = state_value + 1U;
    }
    r.cleanup_address = 0x503a20U;
    r.cleanup_value = 0U;
    r.return_target = 0x18d9cU;
    if (result != (void *)0)
        *result = r;
    return 1;
}
