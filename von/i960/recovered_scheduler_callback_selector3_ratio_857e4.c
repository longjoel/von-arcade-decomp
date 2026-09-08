/* Selector-3 ratio adjustment recovered from i960 0x857e4-0x85844. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_selector3_ratio_857e4 {
    u32 selector;
    s32 value_504dbc;
    float object_ratio;
    u32 ratio_above_165;
    u32 dimensions_match_2_1;
    u32 adjusts_g1_to_1;
    u32 branches_to_85844;
};

struct recovered_scheduler_callback_selector3_ratio_857e4
recovered_scheduler_callback_selector3_ratio_857e4(u32 selector,
                                                   s32 value_504dbc,
                                                   int16_t object_1d0,
                                                   int16_t object_1d8,
                                                   u32 value_g1,
                                                   u32 value_g2)
{
    struct recovered_scheduler_callback_selector3_ratio_857e4 out;

    out.selector = selector;
    out.value_504dbc = value_504dbc;
    out.object_ratio = (float)object_1d0 / (float)object_1d8;
    out.ratio_above_165 = out.object_ratio > 1.65F ? 1U : 0U;
    out.dimensions_match_2_1 = (value_g1 == 2U && value_g2 == 1U) ? 1U : 0U;
    out.adjusts_g1_to_1 = (selector == 3U && value_504dbc <= 32
        && out.ratio_above_165 != 0U && out.dimensions_match_2_1 != 0U) ? 1U : 0U;
    out.branches_to_85844 = selector == 3U ? 0U : 1U;
    return out;
}
