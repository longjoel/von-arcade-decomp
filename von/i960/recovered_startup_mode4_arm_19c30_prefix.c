/* Slot-8 entry prefix recovered from i960 0x19c30-0x19d20. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 register_restore_quad;
    recovered_u32 marker_address, marker_value;
    recovered_u32 workspace_clear_address, workspace_clear_value;
    recovered_u32 setup_call, setup_argument;
    recovered_u32 phase_flag_address, phase_flag_value;
    recovered_u32 phase_flag_helper_call;
    recovered_u32 phase_code, phase_code_address;
    recovered_u32 phase_code_source, phase_code_value;
    recovered_u32 phase_code_sentinel;
    recovered_u32 status_address, status_value, status_threshold;
    recovered_u32 status_above_threshold;
    recovered_u32 record_helper_call, record_helper_first, record_helper_second;
    recovered_u32 result_helper_call, result_helper_argument;
    recovered_u32 ready_address, ready_value;
    recovered_u32 startup_counter_address, startup_counter_value;
    recovered_u32 register_17_value, register_29_value;
    recovered_u32 arithmetic_divisor, arithmetic_constant;
    recovered_u32 arithmetic_remainder, arithmetic_quotient;
    recovered_u32 arithmetic_scaled_remainder, arithmetic_result;
    recovered_u32 math_helper_call, math_result_address;
    recovered_u32 hardware_mode_address, hardware_mode, ready_split;
    recovered_u32 return_or_continuation;
} recovered_startup_mode4_arm_result_19c30_prefix;

int recovered_startup_mode4_arm_19c30_prefix(
    recovered_u32 phase_flag, recovered_u32 status_value,
    recovered_u32 ready_value, recovered_u32 startup_counter,
    recovered_u32 hardware_mode, recovered_u32 register_17_value,
    recovered_u32 register_29_value,
    recovered_startup_mode4_arm_result_19c30_prefix *result)
{
    recovered_startup_mode4_arm_result_19c30_prefix r = {0};
    r.register_restore_quad = 1U;
    r.marker_address = 0x503ab0U;
    r.marker_value = 0xffU;
    r.workspace_clear_address = 0x503a60U;
    r.workspace_clear_value = 0U;
    r.setup_call = 0x2a4e0U;
    r.setup_argument = 2U;
    r.phase_flag_address = 0x503a74U;
    r.phase_flag_value = phase_flag;
    r.phase_flag_helper_call = 0xc8fa0U;
    r.phase_code_address = 0x503ab4U;
    r.phase_code = phase_flag == 0U ? 100U : phase_flag == 1U ? 105U : 110U;
    r.phase_code_source = 0x503a74U;
    r.phase_code_value = r.phase_code;
    r.phase_code_sentinel = 0x258U;
    r.status_address = 0x503a18U;
    r.status_value = status_value;
    r.status_threshold = 0xf423eU;
    r.status_above_threshold = status_value > r.status_threshold ? 1U : 0U;
    r.record_helper_call = 0x1cac8U;
    r.record_helper_first = 6U;
    r.record_helper_second = 3U;
    r.result_helper_call = 0x1e800U;
    r.result_helper_argument = 0U;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.startup_counter_address = 0x503a1cU;
    r.startup_counter_value = startup_counter;
    r.register_17_value = register_17_value;
    r.register_29_value = register_29_value;
    r.arithmetic_constant = 31U + register_17_value;
    r.arithmetic_divisor = startup_counter;
    if (startup_counter != 0U) {
        r.arithmetic_remainder = r.arithmetic_constant % startup_counter;
        r.arithmetic_quotient = r.arithmetic_constant / startup_counter;
        /* lda (g2)[g2*2],g2 followed by shlo 5 and addo g2,g5,g2
         * yields 3*remainder + 96*remainder. */
        r.arithmetic_scaled_remainder = r.arithmetic_remainder * 99U;
        if (r.arithmetic_quotient != 0U)
            r.arithmetic_result = r.arithmetic_scaled_remainder / r.arithmetic_constant;
    }
    r.math_helper_call = 0x1e9e0U;
    r.math_result_address = 0x504c90U;
    r.hardware_mode_address = 0x503a08U;
    r.hardware_mode = hardware_mode;
    r.ready_split = ready_value == 0U ? 1U : 0U;
    r.return_or_continuation = 0x19d20U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
