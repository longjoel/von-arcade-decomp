/* Post-handler frame match recovered from i960 0x8522c-0x8524c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_row_frame_match_8522c {
    u32 row_field_6_low_byte;
    u32 saved_frame_value;
    u32 matches;
    u32 incoming_r7;
    u32 outgoing_r7;
};

struct recovered_scheduler_frame_row_frame_match_8522c
recovered_scheduler_frame_row_frame_match_8522c(u32 row_field_6,
                                                u32 saved_frame_value,
                                                u32 incoming_r7)
{
    struct recovered_scheduler_frame_row_frame_match_8522c out;

    out.row_field_6_low_byte = row_field_6 & 0xffU;
    out.saved_frame_value = saved_frame_value;
    out.matches = out.row_field_6_low_byte == saved_frame_value ? 1U : 0U;
    out.incoming_r7 = incoming_r7;
    out.outgoing_r7 = incoming_r7 + out.matches;
    return out;
}
