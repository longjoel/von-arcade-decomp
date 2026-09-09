/* Sixth phase-table arm recovered from i960 0x196c0-0x19820. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 device_word_address, device_word;
    recovered_u32 primary_marker, primary_command;
    recovered_u32 status_address, status_value, status_command;
    recovered_u32 progress_address, progress_before, progress_after;
    recovered_u32 progress_was_zero, progress_triggered_setup;
    recovered_u32 input_address, input_value, input_mask, input_masked;
    recovered_u32 input_probe_call;
    recovered_u32 setup_call[3], setup_argument[3], setup_count;
    recovered_u32 ready_address, ready_before, ready_after;
    recovered_u32 command_address, command_value;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 workspace_clear_address, workspace_clear_value;
    recovered_u32 workspace_pointer_address, workspace_pointer_value;
    recovered_u32 branch_primary, branch_status, branch_32, fallback_path;
    recovered_u32 return_target;
} recovered_startup_mode4_arm_result_196c0;

int recovered_startup_mode4_arm_196c0(
    recovered_u32 device_word, recovered_u32 primary_marker,
    recovered_u32 status_value, recovered_u32 progress_value,
    recovered_u32 input_value, recovered_u32 ready_value,
    recovered_u32 phase_value,
    recovered_startup_mode4_arm_result_196c0 *result)
{
    recovered_startup_mode4_arm_result_196c0 r = {0};
    r.device_word_address = 0x5024f4U;
    r.device_word = device_word;
    r.primary_marker = primary_marker;
    r.primary_command = primary_marker + 31U;
    r.status_address = 0x503a98U;
    r.status_value = status_value;
    r.status_command = status_value + 31U;
    r.progress_address = 0x503a04U;
    r.progress_before = progress_value;
    r.progress_after = progress_value + 1U;
    r.progress_was_zero = progress_value == 0U ? 1U : 0U;
    r.input_address = 0x5024e8U;
    r.input_value = input_value;
    r.input_mask = 8U;
    r.input_masked = input_value & r.input_mask;
    r.input_probe_call = 0x1fff0U;
    r.setup_call[0] = 0x201a0U;
    r.setup_call[1] = 0x2a4e0U;
    r.setup_call[2] = 0x2a4e0U;
    r.setup_argument[0] = 1U;
    r.setup_argument[1] = 3U;
    r.setup_argument[2] = 0x100bU;
    r.ready_address = 0x503a7cU;
    r.ready_before = ready_value;
    r.ready_after = ready_value;
    r.command_address = 0x5032f4U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = phase_value;
    r.workspace_clear_address = 0x503a20U;
    r.workspace_clear_value = 0U;

    if (device_word == r.primary_command) {
        r.branch_primary = 1U;
        r.setup_count = 0U;
        if (r.progress_was_zero != 0U) {
            r.progress_triggered_setup = 1U;
            r.setup_count = 3U;
            r.command_value = primary_marker + 32U;
            r.ready_after = 1U;
        } else if (r.progress_after == 26U) {
            r.setup_count = 1U;
            r.setup_argument[0] = 0x1325U;
        }
        r.return_target = 0x19740U;
    } else if (device_word == r.status_command) {
        r.branch_status = 1U;
        r.ready_after = 1U;
        r.command_value = 0U;
        r.phase_after = phase_value + 1U;
        r.workspace_pointer_address = 0x503a9cU;
        r.workspace_pointer_value = 0x5024fcU;
        r.workspace_clear_address = 0x503a84U;
        r.workspace_clear_value = 0x5024f8U;
        r.return_target = 0x1979cU;
    } else if (device_word == 32U) {
        r.branch_32 = 1U;
        r.ready_after = 1U;
        r.command_value = 0U;
        r.phase_after = phase_value + 1U;
        r.workspace_pointer_address = 0x503a9cU;
        r.workspace_pointer_value = 0x5024fcU;
        r.return_target = 0x197e8U;
    } else {
        r.fallback_path = 1U;
        r.ready_after = 0U;
        r.command_value = 0U;
        r.phase_after = phase_value + 1U;
        r.workspace_pointer_address = 0x503a9cU;
        r.workspace_pointer_value = 0x5024f8U;
        r.return_target = 0x19820U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
