/* Selector-2 ratio adjustment recovered from i960 0x85784-0x857e4. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_selector2_ratio_85784 {
    u32 selector;
    s32 value_504dc0;
    float object_ratio;
    u32 ratio_above_165;
    u32 dimensions_match_2_2;
    u32 adjusts_g1_to_1;
    u32 branches_to_857e4;
};

struct recovered_scheduler_callback_selector2_ratio_85784
recovered_scheduler_callback_selector2_ratio_85784(u32 selector,
                                                   s32 value_504dc0,
                                                   int16_t object_1d0,
                                                   int16_t object_1d8,
                                                   u32 value_g1,
                                                   u32 value_g2)
{
    struct recovered_scheduler_callback_selector2_ratio_85784 out;

    out.selector = selector;
    out.value_504dc0 = value_504dc0;
    out.object_ratio = (float)object_1d0 / (float)object_1d8;
    out.ratio_above_165 = out.object_ratio > 1.65F ? 1U : 0U;
    out.dimensions_match_2_2 = (value_g1 == 2U && value_g2 == 2U) ? 1U : 0U;
    out.adjusts_g1_to_1 = (selector == 2U && value_504dc0 <= 149
        && out.ratio_above_165 != 0U && out.dimensions_match_2_2 != 0U) ? 1U : 0U;
    out.branches_to_857e4 = selector == 2U ? 0U : 1U;
    return out;
}
