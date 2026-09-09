/* Post-copy service sequence recovered from i960 0x86b0c-0x86b80. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_post_copy_services_86b0c {
    u32 call_count;
    u32 targets[9];
    u32 buffer_arguments[9];
    u32 dynamic_target_503ad4;
    u32 dynamic_target_5040d4;
    u32 continuation;
};

struct recovered_stage_post_copy_services_86b0c
recovered_stage_post_copy_services_86b0c(
    u32 dynamic_target_503ad4, u32 dynamic_target_5040d4)
{
    struct recovered_stage_post_copy_services_86b0c out;

    out.call_count = 9U;
    out.targets[0] = 0x000de990U;
    out.targets[1] = 0x000be1f0U;
    out.targets[2] = 0x000bd730U;
    out.targets[3] = dynamic_target_503ad4;
    out.targets[4] = 0x00023980U;
    out.targets[5] = 0x000df070U;
    out.targets[6] = 0x00026cb8U;
    out.targets[7] = 0x000bd810U;
    out.targets[8] = dynamic_target_5040d4;
    /* 0xde990 inherits the caller's g0; no load is present at 0x86b0c. */
    out.buffer_arguments[0] = UINT32_MAX;
    out.buffer_arguments[1] = 0x00503ad0U;
    out.buffer_arguments[2] = 0x00503ad0U;
    out.buffer_arguments[3] = 0x00503ad0U;
    out.buffer_arguments[4] = 0x00503ad0U;
    out.buffer_arguments[5] = 0x00503ad0U;
    out.buffer_arguments[6] = 0x005040d0U;
    out.buffer_arguments[7] = 0x005040d0U;
    out.buffer_arguments[8] = 0x005040d0U;
    out.dynamic_target_503ad4 = dynamic_target_503ad4;
    out.dynamic_target_5040d4 = dynamic_target_5040d4;
    out.continuation = 0x00086b80U;
    return out;
}
