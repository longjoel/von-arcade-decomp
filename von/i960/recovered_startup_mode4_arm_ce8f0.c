/* Workspace-consumer arm recovered from i960 0xce8f0-0xceab4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 countdown_address, countdown_before, countdown_after;
    recovered_u32 record_result_address, record_index, record_stride;
    recovered_u32 helper_call[3], helper_call_count;
    recovered_u32 record_table_address, record_base;
    recovered_u32 gate_field_4c, gate_field_0c, gate_status_a4, gate_field_4;
    recovered_u32 initialization_gate, initialized_entry_count, entry_stride;
    recovered_u32 entry_base, entry_zero_offset, entry_count_offset;
    recovered_u32 link_source, link_destination, link_count_incremented;
    recovered_u32 record_link_offset[5];
    recovered_u32 record_count_offset, record_count_after;
    recovered_u32 bookkeeping_call, return_target;
} recovered_startup_mode4_arm_result_ce8f0;

int recovered_startup_mode4_arm_ce8f0(
    recovered_u32 record_index, recovered_u32 countdown_value,
    recovered_u32 field_4c, recovered_u32 field_0c,
    recovered_u32 status_a4, recovered_u32 field_4,
    recovered_u32 *result_count,
    recovered_startup_mode4_arm_result_ce8f0 *result)
{
    recovered_startup_mode4_arm_result_ce8f0 r = {0};
    r.countdown_address = 0x51c858U;
    r.countdown_before = countdown_value;
    r.countdown_after = countdown_value == 0U ? 1U : countdown_value;
    r.record_result_address = 0x51c850U;
    r.record_index = record_index;
    r.record_stride = 0x154U;
    r.helper_call[0] = 0xcd5b0U;
    r.helper_call[1] = 0xcd4f0U;
    r.helper_call[2] = 0xce100U;
    r.helper_call_count = 3U;
    r.record_table_address = 0x51c5b0U;
    r.record_base = 0x51c5b0U + 0x154U * record_index;
    r.gate_field_4c = field_4c;
    r.gate_field_0c = field_0c;
    r.gate_status_a4 = status_a4;
    r.gate_field_4 = field_4;
    r.initialization_gate = (field_4c == 0U && field_0c == 0U &&
                             (status_a4 & 0x100U) != 0U && field_4 < 31U) ? 1U : 0U;
    r.initialized_entry_count = r.initialization_gate != 0U ? 9U : 0U;
    r.entry_stride = 0x54U;
    r.entry_base = 0x51bb30U + 0xa8U;
    r.entry_zero_offset = 0U;
    r.entry_count_offset = 0x10U;
    r.link_source = 0x51bb30U;
    r.link_destination = 0x51bb30U;
    r.link_count_incremented = 1U;
    r.record_link_offset[0] = 0x0cU;
    r.record_link_offset[1] = 0x1cU;
    r.record_link_offset[2] = 0x20U;
    r.record_link_offset[3] = 0x24U;
    r.record_link_offset[4] = 0x30U;
    r.record_count_offset = 4U;
    r.record_count_after = field_4 + 1U;
    if (result_count != (void *)0)
        *result_count = r.record_count_after;
    r.bookkeeping_call = 0x22c78U;
    r.return_target = 0xceab4U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
