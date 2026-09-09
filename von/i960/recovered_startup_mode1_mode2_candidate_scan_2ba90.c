/* Mode-2 candidate scan tail recovered from i960 0x2ba90-0x2bb28. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 candidate_count, candidate_first, candidate_last;
    recovered_u32 candidate_stride_words, candidate_stride_bytes;
    recovered_u32 candidate_source_address, candidate_publish_address;
    recovered_u32 candidate_match_value, candidate_delta, candidate_mask;
    recovered_u32 candidate_match_count, selected_candidate, selected_value;
    recovered_u32 published, return_target;
} recovered_startup_mode1_mode2_candidate_scan_result_2ba90;

int recovered_startup_mode1_mode2_candidate_scan_2ba90(
    recovered_u32 candidate_count, const recovered_u32 candidate_values[256],
    recovered_startup_mode1_mode2_candidate_scan_result_2ba90 *result)
{
    recovered_startup_mode1_mode2_candidate_scan_result_2ba90 r = {0};
    r.candidate_count = candidate_count;
    r.candidate_first = candidate_count == 0U ? 0U : candidate_count - 1U;
    r.candidate_last = 0U;
    r.candidate_stride_words = 7U;
    r.candidate_stride_bytes = 0x700U;
    r.candidate_source_address = 0x1a14002U;
    r.candidate_publish_address = 0x1a14002U;
    r.candidate_match_value = 32U;
    r.candidate_delta = 34U;
    r.candidate_mask = 0xffffU;
    r.return_target = 0x2bb28U;
    if (candidate_values != (void *)0) {
        for (recovered_u32 i = r.candidate_first;;) {
            recovered_u32 raw = candidate_values[i];
            recovered_u32 masked_delta = (raw - r.candidate_delta) & r.candidate_mask;
            if (raw == r.candidate_match_value || masked_delta <= 1U) {
                ++r.candidate_match_count;
                r.selected_candidate = i;
                r.selected_value = i;
                r.published = 1U;
                break;
            }
            /* bg at 0x2bb24 repeats only while the decremented index is
             * greater than zero.  Index zero is visited only for count 1. */
            if (i <= 1U)
                break;
            --i;
        }
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
