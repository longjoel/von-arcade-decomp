/* Upload/retry prefix of helper 0x8c970 recovered from i960 0x8c970-0x8ca1c. */
#include "recovered_common.h"
#include <stddef.h>

typedef struct {
    recovered_u32 timing_before, current_offset;
    recovered_u32 current_first_source, current_second_source;
    recovered_u32 timing_after_step, timing_next, next_offset;
    recovered_u32 next_first_source, next_second_source;
    recovered_u32 first_destination, second_destination, bytes;
    recovered_u32 upload_helper, initial_upload_count, retry_upload_count;
    recovered_u32 status_entry_count, max_retry_passes;
    recovered_u32 retry_entry, success_mode_address, success_index_address;
    recovered_u32 failure_mode_value;
} recovered_startup_mode4_arm_result_8c970_upload_phase;

typedef struct {
    recovered_u32 matched;
    recovered_u32 match_index;
    recovered_u32 mode_address, mode_value;
    recovered_u32 timing_address, timing_value;
} recovered_startup_mode4_arm_8c970_status_result;

int recovered_startup_mode4_arm_8c970_upload_phase(
    recovered_u32 timing_value,
    recovered_startup_mode4_arm_result_8c970_upload_phase *result)
{
    recovered_startup_mode4_arm_result_8c970_upload_phase r = {0};
    recovered_u32 next_timing = timing_value + 4U;

    r.timing_before = timing_value;
    r.current_offset = ((timing_value >> 2U) * 3U) << 9U;
    r.current_first_source = 0x51d5f0U + r.current_offset;
    r.current_second_source = 0x5289f0U + r.current_offset;
    r.timing_after_step = next_timing;
    r.timing_next = next_timing > 0x78U ? next_timing - 0x78U : next_timing;
    r.next_offset = ((r.timing_next >> 2U) * 3U) << 9U;
    r.next_first_source = 0x51d5f0U + r.next_offset;
    r.next_second_source = 0x5289f0U + r.next_offset;
    r.first_destination = 0x503ad0U;
    r.second_destination = 0x5040d0U;
    r.bytes = 0x600U;
    r.upload_helper = 0xf5d40U;
    r.initial_upload_count = 2U;
    r.retry_upload_count = 2U;
    r.status_entry_count = 32U;
    r.max_retry_passes = 26U;
    r.retry_entry = 0x8c9ccU;
    r.success_mode_address = 0x51c998U;
    r.success_index_address = 0x51c994U;
    r.failure_mode_value = 0U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}

int recovered_startup_mode4_arm_8c970_scan_status(
    const uint8_t status_bytes[32U * 0x20U], recovered_u32 lower_threshold,
    recovered_u32 upper_threshold, recovered_u32 timing_value,
    recovered_startup_mode4_arm_8c970_status_result *result)
{
    recovered_startup_mode4_arm_8c970_status_result r = {0};
    r.match_index = 32U;
    r.timing_value = timing_value;

    if (status_bytes != (const uint8_t *)0) {
        for (recovered_u32 index = 0U; index < 32U; ++index) {
            recovered_u32 offset = index * 0x20U;
            recovered_u32 masked_status = status_bytes[offset] & 0xffU;
            if (masked_status > lower_threshold &&
                masked_status <= upper_threshold && status_bytes[offset + 1U] == 0U) {
                r.matched = 1U;
                r.match_index = index;
                break;
            }
        }
    }
    if (r.matched) {
        r.mode_address = 0x51c998U;
        r.mode_value = timing_value;
        r.timing_address = 0x51c994U;
    } else {
        r.mode_address = 0x51c9a0U;
        r.mode_value = 0U;
        r.timing_value = 0U;
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
