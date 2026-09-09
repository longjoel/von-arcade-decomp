/* Slot-10 timing gate recovered from i960 0x1a778-0x1a7d0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_address, status_word;
    recovered_u32 phase_address, phase_value;
    recovered_u32 workspace_address, workspace_value;
    recovered_u32 timing_expression, signed_negative;
    recovered_u32 low_three_bits, aligned_negative;
    recovered_u32 helper_address, helper_call_count;
    recovered_u32 helper_argument0, helper_argument1;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1a778_timing_gate_result;

int recovered_startup_mode4_arm_1a778_timing_gate(
    recovered_u32 status_word, recovered_u32 phase_value,
    recovered_startup_mode4_arm_1a778_timing_gate_result *result)
{
    recovered_startup_mode4_arm_1a778_timing_gate_result r = {0};
    uint64_t status_term = (uint64_t)status_word * 48U;
    uint64_t expression = 0xf000U - ((status_term - 48U) - phase_value);
    r.status_address = 0x503a18U;
    r.status_word = status_word;
    r.phase_address = 0x503a14U;
    r.phase_value = phase_value;
    r.workspace_address = 0x504cccU;
    r.timing_expression = (recovered_u32)expression;
    r.workspace_value = r.timing_expression;
    r.signed_negative = (int32_t)r.timing_expression < 0 ? 1U : 0U;
    r.low_three_bits = r.timing_expression & 7U;
    r.aligned_negative = (r.signed_negative != 0U && r.low_three_bits == 0U) ? 1U : 0U;
    r.helper_address = 0x29c58U;
    r.continuation = 0x1a7d0U;
    if (r.aligned_negative != 0U) {
        r.helper_call_count = 1U;
        r.helper_argument0 = (recovered_u32)((int32_t)r.timing_expression / 5);
        r.helper_argument1 = 1U;
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
