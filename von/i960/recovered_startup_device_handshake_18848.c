/* Startup device/status handshake recovered from i960 0x18848-0x18900. */
#include "recovered_common.h"

struct recovered_startup_device_handshake_18848_result {
    recovered_u32 startup_flag;
    recovered_u32 controller_status;
    recovered_u32 ready_status;
    recovered_u32 device_word;
    recovered_u32 gate_entered;
    recovered_u32 mode_before;
    recovered_u32 phase_before;
    recovered_u32 mode_after;
    recovered_u32 phase_after;
    recovered_u32 saved_mode_address;
    recovered_u32 saved_phase_address;
    recovered_u32 command_address;
    recovered_u32 command_value;
    recovered_u32 device_command_address;
    recovered_u32 device_command_value;
    recovered_u32 completion_seen;
    recovered_u32 completion_services;
    recovered_u32 retry_target;
};

int recovered_startup_device_handshake_18848(
    recovered_u32 startup_flag, recovered_u32 controller_status,
    recovered_u32 ready_status, recovered_u32 device_word,
    recovered_u32 mode_value, recovered_u32 phase_value,
    struct recovered_startup_device_handshake_18848_result *result)
{
    struct recovered_startup_device_handshake_18848_result r = {0};

    r.startup_flag = startup_flag;
    r.controller_status = controller_status;
    r.ready_status = ready_status;
    r.device_word = device_word;
    r.mode_before = mode_value;
    r.phase_before = phase_value;
    r.mode_after = mode_value;
    r.phase_after = phase_value;
    r.saved_mode_address = 0x503a0cU;
    r.saved_phase_address = 0x503a10U;
    r.command_address = 0x01400000U;
    r.command_value = 4U;
    r.device_command_address = 0x008000f0U;
    r.device_command_value = 0x0f0fU;
    r.retry_target = 0x187e4U;

    /* The gate at 0x18850 requires a clear startup flag and either
     * controller bit 2 or ready-status bit 0. */
    if (startup_flag == 0U &&
        ((controller_status & 0x4U) != 0U ||
         (ready_status & 0x1U) != 0U)) {
        r.gate_entered = 1U;
        r.mode_after = 5U;
        r.phase_after = 0U;
    }
    if (startup_flag == 0U && device_word == 0x50U) {
        r.completion_seen = 1U;
        r.completion_services = 2U;
        r.retry_target = 0x18724U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
