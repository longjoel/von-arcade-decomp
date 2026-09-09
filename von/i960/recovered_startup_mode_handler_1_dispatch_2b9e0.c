/* Startup mode-table handler 1 recovered from i960 0x2b9e0-0x2bb5c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 hardware_mode_address, hardware_mode;
    recovered_u32 status34_address, status34;
    recovered_u32 status23f2_address, status23f2;
    recovered_u32 status38_address, status38;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 special_phase_value, special_phase_written;
    recovered_u32 command_address, command_value;
    recovered_u32 table_address, table_index, selected_handler;
    recovered_u32 handler_suppressed, indirect_dispatch;
    recovered_u32 mode2_tail_entered, mode2_candidate_address;
    recovered_u32 normal_tail_call, normal_tail_result, normal_tail_returned;
    recovered_u32 clear_helper_call, phase_clear, mode_address, mode_before, mode_after;
    recovered_u32 return_target;
} recovered_startup_mode_handler_1_result_2b9e0;

int recovered_startup_mode_handler_1_dispatch_2b9e0(
    recovered_u32 hardware_mode, recovered_u32 status34, recovered_u32 status23f2,
    recovered_u32 status38, recovered_u32 phase, recovered_u32 mode_value,
    recovered_u32 normal_tail_result, const recovered_u32 table[32],
    recovered_startup_mode_handler_1_result_2b9e0 *result)
{
    recovered_startup_mode_handler_1_result_2b9e0 r = {0};
    r.hardware_mode_address = 0x503a08U;
    r.hardware_mode = hardware_mode;
    r.status34_address = 0x1d00034U;
    r.status34 = status34;
    r.status23f2_address = 0x5023f2U;
    r.status23f2 = status23f2;
    r.status38_address = 0x1d00038U;
    r.status38 = status38;
    r.phase_address = 0x503a00U;
    r.phase_before = phase;
    r.phase_after = phase;
    r.special_phase_value = 29U;
    r.command_address = 0x5032f4U;
    r.command_value = 16U;
    r.table_address = 0x2b960U;
    r.mode2_tail_entered = hardware_mode == 2U ? 1U : 0U;
    r.mode2_candidate_address = 0x5770d0U;
    r.normal_tail_call = hardware_mode == 2U ? 0U : 0x3ba0U;
    r.normal_tail_result = normal_tail_result;
    r.normal_tail_returned = (hardware_mode != 2U && normal_tail_result != 0U) ? 1U : 0U;
    r.clear_helper_call = 0x29c08U;
    r.phase_clear = (hardware_mode != 2U && normal_tail_result == 0U) ? 1U : 0U;
    r.mode_address = 0x5039f4U;
    r.mode_before = mode_value;
    r.mode_after = r.phase_clear != 0U ? mode_value + 1U : mode_value;
    if (hardware_mode != 2U && status34 == 0U &&
        ((status23f2 != 0U && phase != 30U) ||
         (status23f2 == 0U && phase >= 5U && phase <= 28U &&
          status38 != 0U))) {
        r.phase_after = 29U;
        r.special_phase_written = 1U;
    }
    r.table_index = r.phase_after & 31U;
    r.selected_handler = (table != (void *)0) ? table[r.table_index] : 0U;
    r.handler_suppressed = (r.selected_handler == 0U ||
                            (hardware_mode == 2U && r.selected_handler == 0xe3ab0U)) ? 1U : 0U;
    r.indirect_dispatch = r.handler_suppressed == 0U ? 1U : 0U;
    if (r.selected_handler == 0U ||
        (hardware_mode == 2U && r.selected_handler == 0xe3ab0U)) {
        r.phase_after = 1U;
    }
    r.return_target = r.normal_tail_returned != 0U ? 0x2bb5cU : 0x2bb58U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
