/* Slot-12 progress gate recovered from i960 0x1b598-0x1b5d8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 progress_address, progress_before, progress_after;
    recovered_u32 setup_argument, setup_call, setup_requested;
    recovered_u32 high_progress_threshold, high_progress_path;
    recovered_u32 control_address, control_value, control_bit4;
    recovered_u32 countdown_performed, progress_write_address, progress_write_value;
    recovered_u32 countdown_zero, device_gate_target;
} recovered_startup_mode4_arm_result_1b598_progress_gate;

int recovered_startup_mode4_arm_1b598_progress_gate(
    recovered_u32 progress_value, recovered_u32 control_value,
    recovered_startup_mode4_arm_result_1b598_progress_gate *result)
{
    recovered_startup_mode4_arm_result_1b598_progress_gate r = {0};

    r.progress_address = 0x503a04U;
    r.progress_before = progress_value;
    r.progress_after = progress_value;
    r.setup_argument = 3U;
    r.setup_call = 0x2a4e0U;
    r.setup_requested = progress_value == 1U ? 1U : 0U;
    r.high_progress_threshold = 0xafU;
    r.control_address = 0x5024a4U;
    r.control_value = control_value;
    r.control_bit4 = (control_value >> 4) & 1U;
    r.high_progress_path = (int32_t)progress_value >
                           (int32_t)r.high_progress_threshold &&
                           r.control_bit4 != 0U ? 1U : 0U;
    r.countdown_performed = r.high_progress_path == 0U ? 1U : 0U;
    if (r.countdown_performed != 0U)
        r.progress_after = progress_value - 1U;
    r.progress_write_address = r.countdown_performed != 0U ? 0x503a04U : 0U;
    r.progress_write_value = r.countdown_performed != 0U ? r.progress_after : 0U;
    r.countdown_zero = r.countdown_performed != 0U && r.progress_after == 0U ? 1U : 0U;
    r.device_gate_target = r.countdown_zero != 0U || r.high_progress_path != 0U ? 0x1b614U : 0x1b5d8U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
