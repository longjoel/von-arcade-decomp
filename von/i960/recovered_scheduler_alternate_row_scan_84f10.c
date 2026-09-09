/* Alternate scheduler row scan recovered from i960 0x84f10-0x85058. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_alternate_row_scan_84f10 {
    u32 success_85058;
    u32 returns_after_scan;
    u32 selected_row;
    u32 scanned_rows;
};

struct recovered_scheduler_alternate_row_scan_84f10
recovered_scheduler_alternate_row_scan_84f10(
    const u32 row_field_7c[8], const u32 global_matches[8],
    const u32 local_match_counts[8])
{
    struct recovered_scheduler_alternate_row_scan_84f10 out = {
        0U, 1U, 0xffffffffU, 0U
    };
    u32 index;

    for (index = 0U; index < 8U; ++index) {
        out.scanned_rows++;
        if (row_field_7c[index] > 49U
            && local_match_counts[index] > 2U
            && global_matches[index] != 0U) {
            out.success_85058 = 1U;
            out.returns_after_scan = 0U;
            out.selected_row = index;
            break;
        }
    }
    return out;
}
