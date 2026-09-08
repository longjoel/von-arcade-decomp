/* Row-band predicate recovered from i960 0x851c0-0x85200. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_row_band_flag_851c0 {
    u32 row_field_6;
    u32 frame_upper;
    u32 lower_bound;
    u32 upper_bound;
    u32 low_upper_special_case;
    u32 sets_r5;
};

struct recovered_scheduler_frame_row_band_flag_851c0
recovered_scheduler_frame_row_band_flag_851c0(u32 row_field_6,
                                              u32 frame_upper)
{
    struct recovered_scheduler_frame_row_band_flag_851c0 out;
    u32 within_upper;

    out.row_field_6 = row_field_6 & 0xffffU;
    out.frame_upper = frame_upper;
    out.lower_bound = frame_upper - 70U;
    out.upper_bound = frame_upper + 70U;
    out.low_upper_special_case = frame_upper <= 69U ? 1U : 0U;
    within_upper = out.row_field_6 <= out.upper_bound;
    if (!within_upper)
        out.sets_r5 = 0U;
    else if (out.low_upper_special_case)
        out.sets_r5 = 1U;
    else
        out.sets_r5 = out.row_field_6 >= out.lower_bound ? 1U : 0U;
    return out;
}
