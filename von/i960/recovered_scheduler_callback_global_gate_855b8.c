/* Callback global admission gate recovered from i960 0x855b8-0x855f8. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_global_gate_855b8 {
    u32 global_flag;
    s32 value_504dc0;
    s32 value_503a14;
    s32 value_503a18;
    s32 frame_quotient;
    s32 frame_target;
    s32 target_difference;
    u32 exits_to_85678;
    u32 continues_to_object_ratio;
};

struct recovered_scheduler_callback_global_gate_855b8
recovered_scheduler_callback_global_gate_855b8(u32 global_flag,
                                               s32 value_504dc0,
                                               s32 value_503a14,
                                               s32 value_503a18)
{
    struct recovered_scheduler_callback_global_gate_855b8 out;

    out.global_flag = global_flag;
    out.value_504dc0 = value_504dc0;
    out.value_503a14 = value_503a14;
    out.value_503a18 = value_503a18;
    out.frame_quotient = value_503a14 / 48;
    out.frame_target = out.frame_quotient + 1;
    out.target_difference = value_503a18 - out.frame_target;
    out.exits_to_85678 = (global_flag != 0U
        || value_504dc0 > 149
        || out.target_difference >= 20) ? 1U : 0U;
    out.continues_to_object_ratio = out.exits_to_85678 == 0U ? 1U : 0U;
    return out;
}
