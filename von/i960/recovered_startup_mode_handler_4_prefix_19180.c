/* Prefix of startup mode handler 4 recovered from i960 0x19180-0x1922c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 setup_call, setup_call_count;
    recovered_u32 device_register, device_word[2], device_word_count;
    recovered_u32 ready_address, ready_value, ready_required;
    recovered_u32 device_status_address, device_status_value, device_status_required;
    recovered_u32 phase_address, phase_value, phase_low, phase_high;
    recovered_u32 phase_window_passed, special_phase_passed;
    recovered_u32 hardware_word_address, hardware_word_before, hardware_word_after, hardware_mask;
    recovered_u32 hardware_setup_call;
    recovered_u32 marker_address, marker_value;
    recovered_u32 setup_argument[2], setup_argument_count, setup_argument_call;
    recovered_u32 phase_after, ready_after;
    recovered_u32 tail_target;
} recovered_startup_mode_handler_4_prefix_result_19180;

int recovered_startup_mode_handler_4_prefix_19180(
    recovered_u32 ready_value, recovered_u32 device_status,
    recovered_u32 phase_value, recovered_u32 hardware_word,
    recovered_startup_mode_handler_4_prefix_result_19180 *result)
{
    recovered_startup_mode_handler_4_prefix_result_19180 r = {0};
    r.setup_call = 0x295d0U;
    r.setup_call_count = 1U;
    r.device_register = 0x884000U;
    r.device_word[0] = 8U;
    r.device_word[1] = 16U;
    r.device_word_count = 2U;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.ready_required = 0U;
    r.device_status_address = 0x5024f4U;
    r.device_status_value = device_status;
    r.device_status_required = 33U;
    r.phase_address = 0x503a00U;
    r.phase_value = phase_value;
    r.phase_low = 8U;
    r.phase_high = 27U;
    r.phase_window_passed = (phase_value >= 8U && phase_value <= 12U) ? 1U : 0U;
    r.special_phase_passed = (phase_value == 27U) ? 1U : 0U;
    r.hardware_word_address = 0x10000000U;
    r.hardware_word_before = hardware_word;
    r.hardware_mask = 0xfffeU;
    r.hardware_word_after = hardware_word & r.hardware_mask;
    r.hardware_setup_call = 0x2a870U;
    r.marker_address = 0x5032f4U;
    r.marker_value = 32U;
    r.setup_argument[0] = 0x111bU;
    r.setup_argument[1] = 2U;
    r.setup_argument_count = 2U;
    r.setup_argument_call = 0x2a4e0U;
    r.phase_after = (ready_value == 0U && device_status == 33U &&
                     (r.phase_window_passed != 0U || r.special_phase_passed != 0U)) ? 5U : phase_value;
    r.ready_after = (r.phase_after == 5U) ? 1U : ready_value;
    r.tail_target = 0x1922cU;
    if (result != (void *)0)
        *result = r;
    return 1;
}
