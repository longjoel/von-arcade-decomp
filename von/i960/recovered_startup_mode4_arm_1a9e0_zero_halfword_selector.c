/* Slot-10 zero-halfword selector recovered from i960 0x1a9e0-0x1aa20. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 first_address, first_raw, first_zero;
    recovered_u32 second_address, second_raw, second_zero;
    recovered_u32 callback_register;
    recovered_u32 state_address, state_value, command_address, command_value;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 selected, common_service_selected, continuation;
} recovered_startup_mode4_arm_1a9e0_zero_halfword_selector_result;

int recovered_startup_mode4_arm_1a9e0_zero_halfword_selector(
    recovered_u32 first_raw, recovered_u32 second_raw,
    recovered_u32 callback_register, recovered_u32 phase_value,
    recovered_startup_mode4_arm_1a9e0_zero_halfword_selector_result *result)
{
    recovered_startup_mode4_arm_1a9e0_zero_halfword_selector_result r = {0};
    r.first_address = 0x503ca2U;
    r.first_raw = first_raw;
    r.first_zero = (first_raw & 0xffffU) == 0U ? 1U : 0U;
    r.second_address = 0x5042a2U;
    r.second_raw = second_raw;
    r.second_zero = (second_raw & 0xffffU) == 0U ? 1U : 0U;
    r.callback_register = callback_register;
    r.state_address = 0x503ab0U;
    r.command_address = 0x5032f4U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = phase_value;
    r.continuation = 0x1ac50U;
    if (r.first_zero != 0U) {
        r.selected = 1U;
        r.state_value = 1U;
        r.command_value = 0x41U;
    } else if (r.second_zero != 0U) {
        r.selected = 1U;
        r.state_value = callback_register;
        r.command_value = 0x40U;
    } else {
        r.common_service_selected = 1U;
    }
    if (r.selected != 0U) {
        r.phase_after = phase_value + 1U;
        r.continuation = 0x1ac44U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
