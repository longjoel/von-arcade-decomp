/* Seventh phase-table arm recovered from i960 0x19830-0x19b4c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 reset_call, reset_argument, phase_helper_call, phase_helper_argument;
    recovered_u32 ready_address, ready_before, ready_path;
    recovered_u32 phase_source_address, phase_source_value;
    recovered_u32 workspace_clear_address[3], workspace_clear_count;
    recovered_u32 workspace_copy_address[3], workspace_copy_count;
    recovered_u32 maintenance_call;
    recovered_u32 marker_address, marker_value;
    recovered_u32 profile_table_address, profile_table_index;
    recovered_u32 status_byte_address, status_byte, status_mask;
    recovered_u32 status_lookup_address, status_lookup_value;
    recovered_u32 status_publication_address, status_publication_value;
    recovered_u32 secondary_status_address, secondary_status_value;
    recovered_u32 secondary_publication_address, secondary_publication_value;
    recovered_u32 record_publication_address[3], record_publication_count;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 return_target;
} recovered_startup_mode4_arm_result_19830;

int recovered_startup_mode4_arm_19830(
    recovered_u32 ready_value, recovered_u32 phase_value,
    recovered_u32 status_byte, recovered_u32 status_lookup_value,
    recovered_u32 secondary_status_value,
    recovered_startup_mode4_arm_result_19830 *result)
{
    recovered_startup_mode4_arm_result_19830 r = {0};
    r.reset_call = 0x1c618U;
    r.reset_argument = 0U;
    r.phase_helper_call = 0x1ccf8U;
    r.phase_helper_argument = 0U;
    r.ready_address = 0x503a7cU;
    r.ready_before = ready_value;
    r.ready_path = ready_value != 0U ? 1U : 0U;
    r.phase_source_address = 0x503a84U;
    r.phase_source_value = phase_value;
    r.workspace_clear_address[0] = 0x503a70U;
    r.workspace_clear_address[1] = 0x503a74U;
    r.workspace_clear_address[2] = 0x503a6cU;
    r.workspace_clear_count = 3U;
    r.workspace_copy_address[0] = 0x50330aU;
    r.workspace_copy_address[1] = 0x50330cU;
    r.workspace_copy_address[2] = 0x50330eU;
    r.workspace_copy_count = 3U;
    r.maintenance_call = 0x296d0U;
    r.marker_address = 0x503ab0U;
    r.marker_value = 0xffU;
    r.profile_table_address = 0x194a0U;
    r.profile_table_index = phase_value;
    r.status_byte_address = ready_value != 0U ? 0x1d00016U : 0x1d0001aU;
    r.status_byte = status_byte;
    r.status_mask = 0xffU;
    r.status_lookup_address = 0x2250U;
    r.status_lookup_value = status_lookup_value;
    r.status_publication_address = 0x503a18U;
    r.status_publication_value = status_byte == 0xffU ? 0xf423fU : status_lookup_value;
    r.secondary_status_address = ready_value != 0U ? 0x1d0001bU : 0x1d0001fU;
    r.secondary_status_value = secondary_status_value;
    r.secondary_publication_address = 0x503a78U;
    r.secondary_publication_value = secondary_status_value;
    r.record_publication_address[0] = 0x504ca0U;
    r.record_publication_address[1] = 0x504cb0U;
    r.record_publication_address[2] = 0x504cc0U;
    r.record_publication_count = 3U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = phase_value + 1U;
    r.return_target = 0x19b4cU;
    if (result != (void *)0)
        *result = r;
    return 1;
}
