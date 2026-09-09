/* Third phase-table arm recovered from i960 0x19030-0x190c4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 progress_address, progress_before, progress_after;
    recovered_u32 progress_was_zero;
    recovered_u32 reset_call, setup_call, setup_argument, setup_performed;
    recovered_u32 setup_followup_call, setup_followup_argument;
    recovered_u32 input_address, input_value, input_mask, input_masked;
    recovered_u32 input_probe_call;
    recovered_u32 marker_value, command_address, command_value;
    recovered_u32 secondary_command_value;
    recovered_u32 device_word_address, device_word;
    recovered_u32 hardware_mode_address, hardware_mode;
    recovered_u32 device_match, hardware_match_guard;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 phase_incremented, return_target;
} recovered_startup_mode4_arm_result_19030;

int recovered_startup_mode4_arm_19030(
    recovered_u32 progress_value, recovered_u32 marker_value,
    recovered_u32 input_value, recovered_u32 device_word,
    recovered_u32 hardware_mode, recovered_u32 phase_value,
    recovered_startup_mode4_arm_result_19030 *result)
{
    recovered_startup_mode4_arm_result_19030 r = {0};

    r.progress_address = 0x503a04U;
    r.progress_before = progress_value;
    r.progress_after = progress_value + 1U;
    r.progress_was_zero = progress_value == 0U ? 1U : 0U;
    r.reset_call = 0x1c618U;
    r.setup_call = 0x2a4e0U;
    r.setup_argument = 0x100bU;
    r.setup_performed = r.progress_was_zero;
    r.setup_followup_call = 0x201a0U;
    r.setup_followup_argument = 1U;
    r.input_address = 0x5024e8U;
    r.input_value = input_value;
    r.input_mask = 8U;
    r.input_masked = input_value & r.input_mask;
    r.input_probe_call = 0x1fff0U;
    r.marker_value = marker_value;
    r.command_address = 0x5032f4U;
    r.command_value = marker_value + 31U;
    r.secondary_command_value = 0xffffffffU;
    r.device_word_address = 0x5024f4U;
    r.device_word = device_word;
    r.hardware_mode_address = 0x503a08U;
    r.hardware_mode = hardware_mode;
    r.device_match = device_word == r.command_value ? 1U : 0U;
    r.hardware_match_guard = (hardware_mode != 0U && r.device_match != 0U) ? 1U : 0U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_incremented = r.device_match;
    r.phase_after = r.device_match != 0U ? phase_value + 1U : phase_value;
    r.return_target = 0x190c4U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
