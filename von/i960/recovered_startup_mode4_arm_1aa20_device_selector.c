/* Slot-10 ready-side device selector recovered from i960 0x1aa20-0x1aab4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 device_address, device_word;
    recovered_u32 callback_register;
    recovered_u32 state_address, state_value;
    recovered_u32 command_address, command_value;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 selected, continuation;
} recovered_startup_mode4_arm_1aa20_device_selector_result;

int recovered_startup_mode4_arm_1aa20_device_selector(
    recovered_u32 device_word, recovered_u32 callback_register,
    recovered_u32 phase_value,
    recovered_startup_mode4_arm_1aa20_device_selector_result *result)
{
    recovered_startup_mode4_arm_1aa20_device_selector_result r = {0};
    r.device_address = 0x5024f4U;
    r.device_word = device_word;
    r.callback_register = callback_register;
    r.state_address = 0x503ab0U;
    r.command_address = 0x5032f4U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = phase_value;
    r.continuation = 0x1ac50U;
    if (device_word == 0x42U) {
        r.state_value = 2U;
        r.command_value = 0x42U;
        r.selected = 1U;
    } else if (device_word > 0x42U && device_word == 0x43U) {
        r.state_value = 5U;
        r.command_value = 0x43U;
        r.selected = 1U;
    } else if (device_word == 0x40U) {
        r.state_value = 1U;
        r.command_value = 0x41U;
        r.selected = 1U;
    } else if (device_word == 0x41U) {
        r.state_value = callback_register;
        r.command_value = 0x40U;
        r.selected = 1U;
    }
    if (r.selected != 0U) {
        r.phase_after = phase_value + 1U;
        r.continuation = 0x1ac44U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
