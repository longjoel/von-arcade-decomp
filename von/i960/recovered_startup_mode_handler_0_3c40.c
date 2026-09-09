/* Startup mode handler 0 / UI record walker recovered from 0x3c40-0x3d60. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 id, line, text_length, sentinel;
} recovered_startup_ui_record_3c40;

typedef struct {
    recovered_u32 setup_call, device_register, device_command, device_command_count;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 clear_call, record_state_call, record_state_count;
    recovered_u32 table_address, record_count, character_call, character_count;
    recovered_u32 progress_address, progress_before, progress_after;
    recovered_u32 status_address, status_value, table_walk_performed;
    recovered_u32 completion_flag_address, completion_flag_after;
    recovered_u32 mode_address, mode_before, mode_after;
    recovered_u32 return_target;
} recovered_startup_mode_handler_0_result_3c40;

int recovered_startup_mode_handler_0_3c40(
    recovered_u32 phase_value, recovered_u32 status_value,
    recovered_u32 progress_value, recovered_u32 mode_value,
    const recovered_startup_ui_record_3c40 records[64],
    recovered_startup_mode_handler_0_result_3c40 *result)
{
    recovered_startup_mode_handler_0_result_3c40 r = {0};
    r.setup_call = 0x294b0U;
    r.device_register = 0x884000U;
    r.device_command = 8U;
    r.device_command_count = 1U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = phase_value;
    r.clear_call = 0x1c618U;
    r.record_state_call = 0x1ccf8U;
    r.table_address = 0x2ea2918U;
    r.character_call = 0x1cc40U;
    r.progress_address = 0x503a04U;
    r.progress_before = (phase_value == 0U) ? 0x234U : progress_value;
    r.progress_after = r.progress_before - 1U;
    r.status_address = 0x5024d4U;
    r.status_value = status_value;
    r.table_walk_performed = (phase_value == 0U && status_value == 0U) ? 1U : 0U;
    r.completion_flag_address = 0x5024d4U;
    r.completion_flag_after = status_value;
    r.mode_address = 0x5039f4U;
    r.mode_before = mode_value;
    r.mode_after = mode_value;
    r.return_target = 0x3d60U;

    if (r.table_walk_performed != 0U && records != (void *)0) {
        for (recovered_u32 i = 0; i < 64U; ++i) {
            if (records[i].sentinel != 0U)
                break;
            ++r.record_count;
            ++r.record_state_count;
            r.character_count += records[i].text_length;
        }
    }
    if (r.progress_before == 0U) {
        r.completion_flag_after = 1U;
        r.phase_after = 0U;
        r.mode_after = mode_value + 1U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
