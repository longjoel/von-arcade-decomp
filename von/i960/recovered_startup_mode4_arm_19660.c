/* Fifth phase-table arm recovered from i960 0x19660-0x196b8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 reset_call, phase_helper_call, phase_helper_argument;
    recovered_u32 ready_address, ready_value;
    recovered_u32 status_address, status_value;
    recovered_u32 status_command_address, status_command_value;
    recovered_u32 command_address, command_value;
    recovered_u32 command_register_value, ready_adjustment;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 progress_clear_address, progress_clear_value;
    recovered_u32 return_target;
} recovered_startup_mode4_arm_result_19660;

int recovered_startup_mode4_arm_19660(
    recovered_u32 ready_value, recovered_u32 status_value,
    recovered_u32 command_register_value, recovered_u32 phase_value,
    recovered_startup_mode4_arm_result_19660 *result)
{
    recovered_startup_mode4_arm_result_19660 r = {0};
    r.reset_call = 0x1c618U;
    r.phase_helper_call = 0x1ccf8U;
    r.phase_helper_argument = 0U;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.status_address = 0x503a98U;
    r.status_value = status_value;
    r.status_command_address = 0x5032fcU;
    r.status_command_value = status_value;
    r.command_address = 0x5032f4U;
    r.command_register_value = command_register_value;
    r.ready_adjustment = ready_value != 0U ? 1U : 0U;
    r.command_value = command_register_value + 31U + r.ready_adjustment;
    r.progress_clear_address = 0x503a04U;
    r.progress_clear_value = 0U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = phase_value + 1U;
    r.return_target = 0x196b8U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
