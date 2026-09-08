/* Ratio predicate recovered from i960 0x850c0-0x85134. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_ratio_predicate_850c0 {
    float object_ratio;
    float related_ratio;
    float difference;
    u32 exits_to_85128;
    u32 continues_to_85134;
};

struct recovered_scheduler_ratio_predicate_850c0
recovered_scheduler_ratio_predicate_850c0(int16_t object_first,
                                          int16_t object_second,
                                          int16_t related_first,
                                          int16_t related_second)
{
    struct recovered_scheduler_ratio_predicate_850c0 out;

    /* The shifts after ldos preserve the signed low halfword before cvtir. */
    /* divr src1,src2,dst computes src2/src1 on this i960 listing. */
    out.object_ratio = (float)object_first / (float)object_second;
    out.related_ratio = (float)related_first / (float)related_second;
    out.difference = out.object_ratio - out.related_ratio;
    /* cmpr(fp0,0) followed by bge: equality and positive differences exit. */
    out.exits_to_85128 = out.difference >= 0.0F ? 1U : 0U;
    out.continues_to_85134 = out.difference < 0.0F ? 1U : 0U;
    return out;
}
