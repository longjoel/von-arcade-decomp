/* Slot-9 gate prefix recovered from i960 0x1a280-0x1a3fc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 progress_address, progress_before, progress_after;
    recovered_u32 progress_threshold, threshold_match;
    recovered_u32 cleared_address, cleared_value;
    recovered_u32 setup_call, setup_argument, setup_performed;
    recovered_u32 ready_address, ready_value;
    recovered_u32 hardware_mode_address, hardware_mode;
    recovered_u32 device_word_address, device_word;
    recovered_u32 register_18_value, command_address, command_value;
    recovered_u32 ready_marker_address, ready_marker_value;
    recovered_u32 record_helper_call, record_helper_first, record_helper_second;
    recovered_u32 probe_call, probe_argument;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 common_continuation, gate_path;
} recovered_startup_mode4_arm_result_1a280_prefix;

int recovered_startup_mode4_arm_1a280_prefix(
    recovered_u32 progress_value, recovered_u32 ready_value,
    recovered_u32 hardware_mode, recovered_u32 device_word,
    recovered_u32 register_18_value, recovered_u32 phase_value,
    recovered_startup_mode4_arm_result_1a280_prefix *result)
{
    recovered_startup_mode4_arm_result_1a280_prefix r = {0};
    r.progress_address = 0x503a04U;
    r.progress_before = progress_value;
    r.progress_after = progress_value - 1U;
    r.progress_threshold = 31U;
    r.threshold_match = progress_value == 31U ? 1U : 0U;
    r.cleared_address = 0x504cc8U;
    r.cleared_value = 0U;
    r.setup_call = 0x2a4e0U;
    r.setup_argument = 0x131bU;
    r.setup_performed = r.threshold_match;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.hardware_mode_address = 0x503a08U;
    r.hardware_mode = hardware_mode;
    r.device_word_address = 0x5024f4U;
    r.device_word = device_word;
    r.register_18_value = register_18_value;
    r.command_address = 0x5032f4U;
    r.command_value = register_18_value + 31U;
    r.ready_marker_address = 0x503a60U;
    r.ready_marker_value = 0U;
    r.record_helper_call = 0x1cac8U;
    r.probe_call = 0x1fbe0U;
    r.probe_argument = 0U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = phase_value;
    if (ready_value == 0U && hardware_mode == 0U && progress_value == 0U) {
        r.gate_path = 1U;
        r.ready_marker_value = 1U;
        r.record_helper_first = 14U;
        r.record_helper_second = 16U;
    } else if (hardware_mode != 0U && device_word == r.command_value) {
        r.gate_path = 2U;
        r.ready_marker_value = 1U;
        r.ready_value = 1U;
        r.record_helper_first = 14U;
        r.record_helper_second = ready_value == 0U ? 16U : 18U;
    } else if (ready_value != 0U && progress_value == 0U) {
        r.gate_path = 3U;
        r.ready_marker_value = 1U;
        r.record_helper_first = 14U;
        r.record_helper_second = 18U;
    } else if (ready_value == 0U && hardware_mode == 0U && progress_value == 0U) {
        r.gate_path = 1U;
    }
    if (r.gate_path != 0U) {
        r.phase_after = phase_value + 1U;
        r.common_continuation = 0x1a3dcU;
    } else {
        r.common_continuation = 0x1a3fcU;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
