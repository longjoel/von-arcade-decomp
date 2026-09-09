/* Indexed upload phase of helper 0x888f0 recovered from i960 0x888f0-0x88948. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 timing_input, timing_bias, effective_timing;
    recovered_u32 timing_shifted, table_offset;
    recovered_u32 first_source, first_destination, second_source, second_destination;
    recovered_u32 bytes, upload_helper, upload_count, status_scan_count;
} recovered_startup_mode4_arm_result_888f0_indexed_upload_phase;

int recovered_startup_mode4_arm_888f0_indexed_upload_phase(
    recovered_u32 timing_input,
    recovered_startup_mode4_arm_result_888f0_indexed_upload_phase *result)
{
    recovered_startup_mode4_arm_result_888f0_indexed_upload_phase r = {0};
    r.timing_input = timing_input;
    r.timing_bias = 0x78U;
    r.effective_timing = timing_input > 0U ? timing_input + r.timing_bias : timing_input;
    r.timing_shifted = r.effective_timing >> 2U;
    r.table_offset = (r.timing_shifted * 3U) << 9U;
    r.first_source = 0x51d5f0U + r.table_offset;
    r.first_destination = 0x503ad0U;
    r.second_source = 0x5289f0U + r.table_offset;
    r.second_destination = 0x5040d0U;
    r.bytes = 0x600U;
    r.upload_helper = 0xf5d40U;
    r.upload_count = 2U;
    r.status_scan_count = 29U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
