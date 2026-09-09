/* Slot-10 ready/row/phase gate recovered from i960 0x1a690-0x1a778. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value, row_address, row_value;
    recovered_u32 result_r5, phase_address, phase_value, phase_mask;
    recovered_u32 phase_masked, gate_entered, phase_latch;
    recovered_u32 setup_call, setup_call_count, setup_argument;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1a690_ready_phase_gate_result;

int recovered_startup_mode4_arm_1a690_ready_phase_gate(
    recovered_u32 ready_value, recovered_u32 row_value, recovered_u32 result_r5,
    recovered_u32 phase_value,
    recovered_startup_mode4_arm_1a690_ready_phase_gate_result *result)
{
    recovered_startup_mode4_arm_1a690_ready_phase_gate_result r = {0};
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.row_address = 0x503a80U;
    r.row_value = row_value;
    r.result_r5 = result_r5;
    r.phase_address = 0x503a14U;
    r.phase_value = phase_value;
    r.setup_call = 0x2a4e0U;
    r.setup_argument = 0x1340U;
    r.continuation = 0x1a7d0U;
    if (ready_value == 0U && row_value == 9U) {
        r.gate_entered = 1U;
        if ((int32_t)result_r5 <= 0) {
            r.phase_mask = 7U;
            r.phase_masked = phase_value & 7U;
            r.phase_latch = (phase_value & 1U) != 0U ? 1U : 0U;
        } else if (result_r5 <= 2U) {
            r.phase_mask = 15U;
            r.phase_masked = phase_value & 15U;
            r.phase_latch = r.phase_masked <= 7U ? 1U : 0U;
        } else if (result_r5 <= 5U) {
            r.phase_mask = 31U;
            r.phase_masked = phase_value & 31U;
            r.phase_latch = r.phase_masked <= 15U ? 1U : 0U;
        } else {
            r.phase_mask = 63U;
            r.phase_masked = phase_value & 63U;
            r.phase_latch = r.phase_masked <= 15U ? 1U : 0U;
        }
        if (r.phase_masked == 0U)
            r.setup_call_count = 1U;
        r.continuation = 0x1a778U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
