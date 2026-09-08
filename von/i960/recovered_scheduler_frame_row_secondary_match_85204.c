/* Final pre-call row predicate recovered from i960 0x85204-0x8521c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_row_secondary_match_85204 {
    u32 row_field_4;
    u32 frame_g9_low;
    u32 matches;
    u32 incoming_r5;
    u32 outgoing_r5;
};

struct recovered_scheduler_frame_row_secondary_match_85204
recovered_scheduler_frame_row_secondary_match_85204(u32 row_field_4,
                                                    u32 frame_g9,
                                                    u32 incoming_r5)
{
    struct recovered_scheduler_frame_row_secondary_match_85204 out;

    out.row_field_4 = row_field_4 & 0xffffU;
    out.frame_g9_low = frame_g9 & 0xffffU;
    out.matches = out.row_field_4 == out.frame_g9_low ? 1U : 0U;
    out.incoming_r5 = incoming_r5;
    out.outgoing_r5 = incoming_r5 + out.matches;
    return out;
}
