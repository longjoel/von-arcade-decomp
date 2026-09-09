/* Frame-scan prefix recovered from i960 0x85134-0x851a8. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_scan_prefix_85134 {
    u32 frame_record_address;
    u32 table_base;
    u32 table_field_address;
    u32 frame_upper_g8;
    u32 frame_upper_g9;
    u32 frame_target_g8;
    u32 frame_target_g9;
    u32 field_86;
    u32 exits_to_853a0;
    u32 continues_to_851a8;
};

struct recovered_scheduler_frame_scan_prefix_85134
recovered_scheduler_frame_scan_prefix_85134(u32 frame_slot,
                                            u32 object_state,
                                            u32 frame_g8,
                                            u32 frame_g9,
                                            u32 table_field_86)
{
    struct recovered_scheduler_frame_scan_prefix_85134 out;

    out.frame_record_address = 0x005096a0U + frame_slot * 16U;
    /* lda (state)[state*16], then shlo 6: state * 17 * 64. */
    out.table_base = 0x005074a0U + object_state * 1088U;
    out.table_field_address = out.table_base + 0x86U;
    out.frame_upper_g8 = frame_g8 >> 16;
    out.frame_upper_g9 = frame_g9 >> 16;
    out.frame_target_g8 = out.frame_upper_g8 - 70U;
    out.frame_target_g9 = out.frame_upper_g9 - 70U;
    out.field_86 = table_field_86 & out.frame_upper_g8;
    /* cmpo 49,field followed by bge: fields <= 49 skip the scan. */
    out.exits_to_853a0 = out.field_86 <= 49U ? 1U : 0U;
    out.continues_to_851a8 = out.field_86 > 49U ? 1U : 0U;
    return out;
}
