/* Startup mode-handler slot 7 recovered from i960 0xf3d30-f3ebc. */
#include "recovered_common.h"
#include <stdint.h>

typedef struct {
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 saved_status_address, saved_status;
    recovered_u32 timing_call, timing_result, timing_limit;
    recovered_u32 timing_state_address, timing_state_after;
    recovered_u32 clear_address[3], clear_count;
    recovered_u32 message_call, message_count;
    recovered_u32 message_x[5], message_y[5], message_string[5];
    recovered_u32 gate_call, gate_result, reset_call;
    recovered_u32 terminal_service_count;
    recovered_u32 startup_flag_address, startup_flag_after;
    recovered_u32 device_command_address, device_command;
    recovered_u32 saved_state_address, saved_state;
    recovered_u32 cmpible_taken, cmpibl_taken, transition_mode_value;
    recovered_u32 transition_mode_address, transition_phase_address;
    recovered_u32 return_target;
} recovered_startup_mode_handler_7_result_f3d30;

int recovered_startup_mode_handler_7_f3d30(
    recovered_u32 phase, recovered_u32 saved_status, recovered_u32 timing_result,
    recovered_u32 gate_result, recovered_u32 device_command,
    recovered_u32 saved_state,
    recovered_startup_mode_handler_7_result_f3d30 *result)
{
    recovered_startup_mode_handler_7_result_f3d30 r = {0};
    r.phase_address = 0x503a00U;
    r.phase_before = phase;
    r.phase_after = phase;
    r.saved_status_address = 0x5785b4U;
    r.saved_status = saved_status;
    r.timing_call = 0x20a0U;
    r.timing_result = timing_result;
    r.timing_limit = 0x2710U;
    r.timing_state_address = 0x5785c8U;
    r.timing_state_after = timing_result;
    r.clear_address[0] = 0x5024c4U;
    r.clear_address[1] = 0x5024c6U;
    r.clear_address[2] = 0x5024c8U;
    r.clear_count = 3U;
    r.message_call = 0xeaeb0U;
    r.gate_call = 0xeade8U;
    r.reset_call = 0x1c618U;
    r.startup_flag_address = 0x5039f0U;
    r.startup_flag_after = 0U;
    r.device_command_address = 0x5770b0U;
    r.device_command = device_command;
    r.saved_state_address = 0x503a0cU;
    r.saved_state = saved_state;
    r.transition_mode_address = 0x5039f4U;
    r.transition_phase_address = 0x503a00U;
    r.return_target = 0xf3ec0U;

    if (phase == 0U) {
        r.timing_state_after = 0U;
        if (saved_status != 0U && timing_result > r.timing_limit) {
            static const recovered_u32 strings[5] = {
                0xf3ca0U, 0xf3cc0U, 0xf3ce0U, 0xf3d00U, 0xf3d10U
            };
            static const recovered_u32 y[5] = {15U, 20U, 22U, 24U, 32U};
            r.message_count = 5U;
            for (recovered_u32 i = 0; i < 5U; ++i) {
                r.message_x[i] = 16U;
                r.message_y[i] = y[i];
                r.message_string[i] = strings[i];
            }
            r.phase_after = 1U;
        } else {
            r.phase_after = 2U;
        }
    } else if (phase == 1U) {
        r.gate_result = gate_result;
        if (gate_result == 0U) {
            r.phase_after = phase + 1U;
        }
    } else {
        r.terminal_service_count = 3U;
        /* Literal-first i960 comparisons: cmpible 0,g4 branches for g4 >= 0;
         * cmpibl 0,g4 branches for g4 > 0.  The latter is unreachable after
         * the former, but retaining it preserves the listing's control flow. */
        r.cmpible_taken = ((int32_t)saved_state >= 0) ? 1U : 0U;
        r.cmpibl_taken = ((int32_t)saved_state > 0) ? 1U : 0U;
        if (saved_status == 0U || device_command == 0U)
            r.transition_mode_value = 0xffffffffU;
        else if (r.cmpible_taken != 0U)
            r.transition_mode_value = 0xffffffffU;
        else if (r.cmpibl_taken != 0U)
            r.transition_mode_value = 1U;
        else
            r.transition_mode_value = 0U;
        r.phase_after = 0U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
