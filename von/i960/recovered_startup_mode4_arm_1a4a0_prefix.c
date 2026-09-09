/* Slot-10 timing prefix recovered from i960 0x1a4a0-0x1a578. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 hardware_mode_address, hardware_mode;
    recovered_u32 pending_address, pending_value;
    recovered_u32 timing_address, timing_before, timing_after;
    recovered_u32 timing_threshold, threshold_exceeded;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 fixed_timing_pointer, fixed_workspace_pointer;
    recovered_u32 timing_publication_address, timing_publication_value;
    recovered_u32 workspace_publication_address, workspace_publication_value;
    recovered_u32 common_completion_call, return_target;
} recovered_startup_mode4_arm_result_1a4a0_prefix;

int recovered_startup_mode4_arm_1a4a0_prefix(
    recovered_u32 ready_value, recovered_u32 hardware_mode,
    recovered_u32 pending_value, recovered_u32 timing_value,
    recovered_u32 phase_value,
    recovered_startup_mode4_arm_result_1a4a0_prefix *result)
{
    recovered_startup_mode4_arm_result_1a4a0_prefix r = {0};
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.hardware_mode_address = 0x503a08U;
    r.hardware_mode = hardware_mode;
    r.pending_address = 0x504cc8U;
    r.pending_value = pending_value;
    r.timing_address = 0x503a20U;
    r.timing_before = timing_value;
    r.timing_after = timing_value;
    r.timing_threshold = 0xeffU;
    r.phase_address = 0x503a14U;
    r.phase_before = phase_value;
    r.phase_after = phase_value;
    if (ready_value == 0U && hardware_mode != 0U) {
        r.fixed_timing_pointer = 0x5024feU;
        r.fixed_workspace_pointer = 0x502500U;
        r.timing_after = 0U;
    } else {
        r.threshold_exceeded = (int32_t)timing_value >
                               (int32_t)r.timing_threshold ? 1U : 0U;
        r.phase_after = phase_value + 1U;
        if (r.threshold_exceeded != 0U)
            r.timing_after = 0xf00U;
        else
            r.timing_after = timing_value + 1U;
    }
    if (ready_value == 0U && hardware_mode == 0U && pending_value != 0U) {
        /* The pending branch jumps directly to publication at 0x1a558. */
        r.threshold_exceeded = 0U;
        r.fixed_timing_pointer = 0U;
        r.fixed_workspace_pointer = 0U;
        r.phase_after = phase_value;
        r.timing_after = timing_value;
    }
    r.timing_publication_address = 0x5032feU;
    r.timing_publication_value = (recovered_u32)
        recovered_sign_extend_16(r.phase_after & 0xffffU);
    r.workspace_publication_address = 0x503300U;
    r.workspace_publication_value = (recovered_u32)
        recovered_sign_extend_16(r.timing_after & 0xffffU);
    if (ready_value == 0U && hardware_mode != 0U) {
        /* The fixed-pointer branch returns through 0x1a578, before 0x1a558. */
        r.timing_publication_address = 0U;
        r.timing_publication_value = 0U;
        r.workspace_publication_address = 0U;
        r.workspace_publication_value = 0U;
    }
    r.common_completion_call = 0x43ee8U;
    r.return_target = 0x1a578U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
