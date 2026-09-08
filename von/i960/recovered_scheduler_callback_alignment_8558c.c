/* Callback alignment predicate recovered from i960 0x8558c-0x855b8. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_alignment_8558c {
    u32 incoming_value;
    u32 aligned_value;
    s32 alignment_delta;
    u32 uses_fallback_8;
    u32 continues_with_decoded_dimensions;
};

struct recovered_scheduler_callback_alignment_8558c
recovered_scheduler_callback_alignment_8558c(u32 incoming_value)
{
    struct recovered_scheduler_callback_alignment_8558c out;
    u32 aligned;

    out.incoming_value = incoming_value;
    if ((s32)incoming_value > 0)
        aligned = (incoming_value + 3U) & ~3U;
    else
        aligned = incoming_value & ~3U;
    out.aligned_value = aligned;
    /* subo aligned,original computes original - aligned. */
    out.alignment_delta = (s32)(incoming_value - aligned);
    /* cmpibge 1,delta continues only when delta >= 1. */
    out.uses_fallback_8 = out.alignment_delta < 1 ? 1U : 0U;
    out.continues_with_decoded_dimensions = out.alignment_delta >= 1 ? 1U : 0U;
    return out;
}
