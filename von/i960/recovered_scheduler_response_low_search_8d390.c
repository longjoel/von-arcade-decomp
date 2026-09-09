/* Low-response reverse search recovered from i960 0x8d390-0x8d3ec. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 high_byte, column_offset;
    recovered_u32 row_count, initial_row;
    recovered_u32 probes;
    recovered_u32 matched, matched_row, result_value;
    recovered_u32 table_base, row_stride;
    recovered_u32 failure_result;
} recovered_scheduler_response_low_search_8d390_result;

int recovered_scheduler_response_low_search_8d390(
    recovered_u32 high_byte, recovered_u32 initial_row,
    const uint8_t row_values[30U],
    recovered_scheduler_response_low_search_8d390_result *result)
{
    recovered_scheduler_response_low_search_8d390_result r = {0};
    r.high_byte = high_byte & 0xffU;
    r.column_offset = r.high_byte << 5U;
    r.row_count = 30U;
    r.initial_row = initial_row % r.row_count;
    r.probes = 30U;
    r.matched_row = 30U;
    r.table_base = 0x51d7f0U;
    r.row_stride = 0x600U;
    r.failure_result = 0xffffffffU;

    if (row_values != (const uint8_t *)0) {
        for (recovered_u32 probe = 0U; probe < r.row_count; ++probe) {
            recovered_u32 row = (r.initial_row + r.row_count - probe) % r.row_count;
            if (row_values[row] == 0U) {
                r.probes = probe;
                r.matched = 1U;
                r.matched_row = row;
                r.result_value = probe;
                break;
            }
        }
    }
    if (!r.matched)
        r.result_value = r.failure_result;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
