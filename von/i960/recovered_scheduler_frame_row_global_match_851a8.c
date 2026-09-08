/* First row predicate recovered from i960 0x851a8-0x851c0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_row_global_match_851a8 {
    u32 row_field_0;
    u32 global_504d68;
    u32 matches;
    u32 r7_after_compare;
};

struct recovered_scheduler_frame_row_global_match_851a8
recovered_scheduler_frame_row_global_match_851a8(u32 row_field_0,
                                                 u32 value_504d68)
{
    struct recovered_scheduler_frame_row_global_match_851a8 out;

    out.row_field_0 = row_field_0 & 0xffffU;
    out.global_504d68 = value_504d68;
    out.matches = out.row_field_0 == value_504d68 ? 1U : 0U;
    /* The assembly initializes r7 to zero immediately before this test. */
    out.r7_after_compare = out.matches;
    return out;
}
