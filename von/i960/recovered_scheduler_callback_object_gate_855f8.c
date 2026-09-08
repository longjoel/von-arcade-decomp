/* Object-ratio gate recovered from i960 0x855f8-0x85634. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_object_gate_855f8 {
    s32 object_1d0;
    s32 object_1d8;
    s32 shifted_1d8;
    s32 target_difference;
    u32 value_5024e8;
    u32 remainder_300;
    u32 ratio_rejected;
    u32 remainder_checked;
    u32 forces_dimensions_1_1;
    u32 continues_to_85634;
};

struct recovered_scheduler_callback_object_gate_855f8
recovered_scheduler_callback_object_gate_855f8(s32 object_1d0,
                                               s32 object_1d8,
                                               s32 target_difference,
                                               u32 value_5024e8)
{
    struct recovered_scheduler_callback_object_gate_855f8 out;

    out.object_1d0 = object_1d0;
    out.object_1d8 = object_1d8;
    out.shifted_1d8 = object_1d8 >> 2;
    out.target_difference = target_difference;
    out.value_5024e8 = value_5024e8;
    out.remainder_300 = value_5024e8 % 300U;
    out.ratio_rejected = object_1d0 <= out.shifted_1d8 ? 1U : 0U;
    out.remainder_checked = target_difference > 45 ? 1U : 0U;
    out.forces_dimensions_1_1 = (out.remainder_checked
        && out.remainder_300 > 45U) ? 1U : 0U;
    out.continues_to_85634 = out.ratio_rejected == 0U ? 1U : 0U;
    return out;
}
