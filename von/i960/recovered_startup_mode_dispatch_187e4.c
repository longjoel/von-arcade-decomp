/* Startup mode-table selector recovered from i960 0x18800-0x18844. */
#include "recovered_common.h"

struct recovered_startup_mode_dispatch_187e4_result {
    recovered_u32 table_address;
    recovered_u32 mode_address;
    recovered_u32 phase_address;
    recovered_u32 mode_before;
    recovered_u32 mode_index;
    recovered_u32 selected_target;
    recovered_u32 callx_performed;
    recovered_u32 null_target_repaired;
    recovered_u32 mode_after;
    recovered_u32 phase_after;
    recovered_u32 continuation;
};

int recovered_startup_mode_dispatch_187e4(
    recovered_u32 mode_value, const recovered_u32 handlers[16],
    struct recovered_startup_mode_dispatch_187e4_result *result)
{
    struct recovered_startup_mode_dispatch_187e4_result r = {0};

    r.table_address = 0x18680U;
    r.mode_address = 0x5039f4U;
    r.phase_address = 0x503a00U;
    r.mode_before = mode_value;
    r.mode_index = mode_value & 0xfU;
    r.mode_after = mode_value;
    r.phase_after = 0U;
    r.continuation = 0x18848U;

    if (handlers == (void *)0)
        return 0;
    r.selected_target = handlers[r.mode_index];
    if (r.selected_target == 0U) {
        /* The null-entry arm at 0x18834 repairs the mode before the
         * common device/status continuation at 0x18848. */
        r.null_target_repaired = 1U;
        r.mode_after = 1U;
    } else {
        r.callx_performed = 1U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
