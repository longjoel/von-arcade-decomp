/* Status-table scan recovered from i960 0x8ca1c-0x8ca80. */
#include "recovered_common.h"
#include <stddef.h>

typedef struct {
    recovered_u32 status_table;
    recovered_u32 lower_threshold;
    recovered_u32 upper_threshold;
    recovered_u32 first_status;
    recovered_u32 first_status_masked;
    recovered_u32 first_status_next;
    recovered_u32 matched;
    recovered_u32 match_index;
    recovered_u32 match_address;
    recovered_u32 match_count;
    recovered_u32 no_match_address;
    recovered_u32 no_match_value;
    recovered_u32 entry_count;
    recovered_u32 entry_stride;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8ca1c_status_scan_result;

recovered_startup_mode4_arm_8ca1c_status_scan_result
recovered_startup_mode4_arm_8ca1c_status_scan(
    recovered_u32 status_table, const uint8_t status_bytes[32U * 0x20U],
    recovered_u32 lower_threshold, recovered_u32 upper_threshold)
{
    recovered_startup_mode4_arm_8ca1c_status_scan_result result = {0};

    result.status_table = status_table;
    result.lower_threshold = lower_threshold;
    result.upper_threshold = upper_threshold;
    result.match_index = 32U;
    result.no_match_address = 0x51c9a0U;
    result.no_match_value = 0U;
    result.entry_count = 32U;
    result.entry_stride = 0x20U;
    result.continuation = 0x0008ca80U;
    if (status_bytes != (const uint8_t *)0) {
        result.first_status = status_bytes[0];
        result.first_status_masked = status_bytes[0] & 0xffU;
        result.first_status_next = status_bytes[1];
        for (recovered_u32 index = 0U; index < 32U; ++index) {
            recovered_u32 offset = index * 0x20U;
            recovered_u32 masked_status = status_bytes[offset] & 0xffU;
            if (masked_status > lower_threshold &&
                masked_status <= upper_threshold && status_bytes[offset + 1U] == 0U) {
                result.matched = 1U;
                result.match_index = index;
                result.match_address = status_table + offset;
                result.match_count = index + 1U;
                return result;
            }
        }
    }
    return result;
}
