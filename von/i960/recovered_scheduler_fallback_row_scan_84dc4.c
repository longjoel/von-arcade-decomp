/* Fallback row scan recovered from i960 0x84dc4-0x84f10. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_fallback_row_scan_84dc4 {
    u32 success_84dac;
    u32 continues_84f10;
    u32 selected_row;
    u32 scanned_rows;
};

struct recovered_scheduler_fallback_row_scan_84dc4
recovered_scheduler_fallback_row_scan_84dc4(
    const u32 row_field_86[8], const u32 global_matches[8],
    const u32 local_match_counts[8])
{
    struct recovered_scheduler_fallback_row_scan_84dc4 out = {
        0U, 1U, 0xffffffffU, 0U
    };
    u32 index;

    for (index = 0U; index < 8U; ++index) {
        out.scanned_rows++;
        if (row_field_86[index] > 49U
            && local_match_counts[index] > 2U
            && global_matches[index] != 0U) {
            out.success_84dac = 1U;
            out.continues_84f10 = 0U;
            out.selected_row = index;
            break;
        }
    }
    return out;
}
