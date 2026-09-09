/* Second phase-table arm recovered from i960 0x18da0-0x19028. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 record_state_call, record_state_first, record_state_second;
    recovered_u32 formatter_call, formatter_argument, formatter_call_count;
    recovered_u32 progress_address, progress_before, progress_after;
    recovered_u32 counter_address, counter_before, counter_after;
    recovered_u32 divisor, device_word_address, device_word;
    recovered_u32 check_mask, checks_required, checks_passed;
    recovered_u32 status_a4, status_a5, status_a6;
    recovered_u32 status_gate, extended_status_gate;
    recovered_u32 setup_call, setup_argument, setup_performed;
    recovered_u32 ready_address, ready_before, ready_after;
    recovered_u32 command_address, command_value, secondary_command_value;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 progress_limit_reached, counter_path, fallback_path;
    recovered_u32 return_target;
} recovered_startup_mode4_arm_result_18da0;

int recovered_startup_mode4_arm_18da0(
    recovered_u32 record_value, recovered_u32 counter_value,
    recovered_u32 progress_value, recovered_u32 device_word,
    recovered_u32 check_mask, recovered_u32 status_a4,
    recovered_u32 status_a5, recovered_u32 status_a6,
    recovered_u32 ready_value, recovered_u32 phase_value,
    recovered_startup_mode4_arm_result_18da0 *result)
{
    recovered_startup_mode4_arm_result_18da0 r = {0};
    r.record_state_call = 0x1cac8U;
    r.record_state_first = 28U;
    r.record_state_second = 29U;
    r.formatter_call = 0x1ebb0U;
    r.formatter_argument = record_value + 31U;
    r.formatter_call_count = 1U;
    r.progress_address = 0x503a04U;
    r.progress_before = progress_value;
    r.progress_after = progress_value;
    r.counter_address = 0x504c94U;
    r.counter_before = counter_value;
    r.counter_after = counter_value;
    r.divisor = r.formatter_argument;
    r.device_word_address = 0x5024f4U;
    r.device_word = device_word;
    r.check_mask = check_mask;
    r.checks_required = 7U;
    r.checks_passed = 0U;
    for (recovered_u32 i = 0; i < 7U; ++i)
        if ((check_mask & (1U << i)) != 0U)
            ++r.checks_passed;
    r.status_a4 = status_a4;
    r.status_a5 = status_a5;
    r.status_a6 = status_a6;
    r.ready_address = 0x503a7cU;
    r.ready_before = ready_value;
    r.ready_after = ready_value;
    r.command_address = 0x5032f4U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = phase_value;

    if (counter_value == 0U) {
        if (progress_value != 0U)
            r.progress_after = progress_value - 1U;
        r.progress_limit_reached = r.progress_after > 0x27fU ? 1U : 0U;
        r.status_gate = ((status_a5 & 1U) != 0U ||
                         (status_a6 & 1U) != 0U ||
                         (status_a4 & 0x10U) != 0U) ? 1U : 0U;
        r.extended_status_gate = (((status_a5 & 0x40U) != 0U) ||
                                  ((status_a6 & 0x40U) != 0U)) ? 1U : 0U;
        if (device_word == 16U || r.checks_passed != r.checks_required) {
            r.command_value = 31U + counter_value;
            r.ready_after = 0U;
            r.fallback_path = 1U;
            r.counter_after = counter_value + 1U;
        } else if (r.status_gate != 0U && r.progress_limit_reached == 0U) {
            r.setup_call = 0x2a4e0U;
            r.setup_argument = 0x1111U;
            r.setup_performed = 1U;
            r.command_value = ready_value == 0U ? 31U + 0x52U : 31U + ready_value;
            r.secondary_command_value = ready_value == 0U ? 0xffffffffU : 0U;
            r.counter_after = counter_value + 1U;
        } else if (r.extended_status_gate != 0U && ready_value != 0U) {
            r.ready_after = 0U;
            r.setup_call = 0x2a4e0U;
            r.setup_argument = 0x1100U;
            r.setup_performed = 1U;
        } else if ((status_a5 & 0x80U) != 0U ||
                   (status_a6 & 0x80U) != 0U) {
            if (ready_value == 0U) {
                r.ready_after = 1U;
                r.setup_call = 0x2a4e0U;
                r.setup_argument = 0x1100U;
                r.setup_performed = 1U;
            }
        }
        r.return_target = 0x18fa4U;
    } else {
        r.counter_path = 1U;
        r.ready_after = ready_value;
        r.counter_after = counter_value + 1U;
        if (r.counter_after <= r.divisor) {
            r.return_target = 0x19028U;
        } else if (ready_value == 0U) {
            r.command_value = phase_value + 31U;
            r.secondary_command_value = 0xffffffffU;
            r.progress_after = 0U;
            r.phase_after = phase_value + 1U;
            r.return_target = 0x1900cU;
        } else {
            r.command_value = phase_value + 31U;
            r.phase_after = 3U;
            r.return_target = 0x19028U;
        }
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
