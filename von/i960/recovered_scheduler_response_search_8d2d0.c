/* Normal response search skeleton recovered from i960 0x8d2d0-0x8d390. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 response_delta;
    recovered_u32 response_bias, status_entry_count;
    recovered_u32 row_count, initial_row;
    recovered_u32 attempts;
    recovered_u32 matched, matched_row, result_value;
    recovered_u32 low_response_target;
    recovered_u32 failure_result;
} recovered_scheduler_response_search_8d2d0_result;

typedef struct {
    recovered_u32 lower_threshold, upper_threshold;
    recovered_u32 status_entry_count, status_stride;
    recovered_u32 row_count, row_stride, initial_row;
    recovered_u32 attempts, matched, matched_row, result_value;
    recovered_u32 failure_result;
} recovered_scheduler_response_search_8d2d0_status_result;

int recovered_scheduler_response_search_8d2d0(
    recovered_u32 response_delta, recovered_u32 initial_row,
    const uint8_t row_matches[30U],
    recovered_scheduler_response_search_8d2d0_result *result)
{
    recovered_scheduler_response_search_8d2d0_result r = {0};
    r.response_delta = response_delta;
    r.response_bias = 0x25U;
    r.status_entry_count = 32U;
    r.row_count = 30U;
    /* 0x8d2dc advances g6 before the first normal-table probe. */
    r.initial_row = (initial_row + 1U) % r.row_count;
    r.attempts = 30U;
    r.matched_row = 30U;
    r.low_response_target = 0x8d390U;
    r.failure_result = 0xffffffffU;

    if (response_delta >= 5U && row_matches != (const uint8_t *)0) {
        for (recovered_u32 attempt = 0U; attempt < r.row_count; ++attempt) {
            recovered_u32 row = (r.initial_row + attempt) % r.row_count;
            if (row_matches[row] != 0U) {
                r.attempts = attempt + 1U;
                r.matched = 1U;
                r.matched_row = row;
                r.result_value = 30U - attempt;
                break;
            }
        }
    }
    if (!r.matched)
        r.result_value = r.failure_result;
    return result != (void *)0 ? (*result = r, 1) : 1;
}

int recovered_scheduler_response_search_8d2d0_scan_status(
    recovered_u32 lower_input, recovered_u32 upper_input,
    recovered_u32 initial_row, const uint8_t status_table[30U * 0x600U],
    recovered_scheduler_response_search_8d2d0_status_result *result)
{
    recovered_scheduler_response_search_8d2d0_status_result r = {0};
    r.lower_threshold = lower_input + 31U;
    r.upper_threshold = upper_input + 31U;
    r.status_entry_count = 32U;
    r.status_stride = 0x20U;
    r.row_count = 30U;
    r.row_stride = 0x600U;
    /* The normal arm increments g6 before forming the first row address. */
    r.initial_row = (initial_row + 1U) % r.row_count;
    r.attempts = r.row_count;
    r.matched_row = r.row_count;
    r.failure_result = 0xffffffffU;

    if (status_table != (const uint8_t *)0) {
        for (recovered_u32 attempt = 0U; attempt < r.row_count; ++attempt) {
            recovered_u32 row = (r.initial_row + attempt) % r.row_count;
            const uint8_t *row_base = status_table + row * r.row_stride;
            for (recovered_u32 entry = 0U; entry < r.status_entry_count; ++entry) {
                const uint8_t *slot = row_base + entry * r.status_stride;
                recovered_u32 masked_status = slot[0] & 0xffU;
                if (masked_status > r.lower_threshold &&
                    masked_status <= r.upper_threshold && slot[1] == 0U) {
                    r.attempts = attempt + 1U;
                    r.matched = 1U;
                    r.matched_row = row;
                    r.result_value = 30U - attempt;
                    return result != (void *)0 ? (*result = r, 1) : 1;
                }
            }
        }
    }
    r.result_value = r.failure_result;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
