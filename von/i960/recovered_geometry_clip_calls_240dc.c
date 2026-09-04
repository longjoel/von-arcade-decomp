/* Four geometry clip calls recovered from i960 0x240dc-0x2422c. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_geometry_clip_calls_plan {
    u32 clip_dispatch;
    u32 frame_zero_offset;
    u32 frame_selected_offset;
    u32 frame_constants[2];
    u32 control_address;
    u32 control_value;
    u32 frame_publish_address;
    u32 frame_publish_offset;
    u32 call_count;
    u32 call_argument[4][7];
};

void recovered_geometry_clip_calls_plan(
    u32 derived_clip_word, u32 fourth_call_g0,
    struct recovered_geometry_clip_calls_plan *plan)
{
    static const u32 one = RECOVERED_FLOAT_ONE;
    static const u32 geometry_base = 0x400028U;

    RECOVERED_SET_CLIP_PLAN_COMMON(plan);
    plan->frame_zero_offset = 0xc0U;
    plan->frame_selected_offset = 0xc4U;
    plan->frame_publish_offset = 0x400028U;

    plan->call_argument[0][0] = 0xc2040000U;
    plan->call_argument[0][1] = 0x43310000U;
    plan->call_argument[0][2] = one;
    plan->call_argument[0][3] = derived_clip_word;
    plan->call_argument[0][4] = 0x43310000U;
    plan->call_argument[0][5] = one;
    plan->call_argument[0][6] = geometry_base;

    plan->call_argument[1][0] = 0xc2040000U;
    plan->call_argument[1][1] = 0x431f0000U;
    plan->call_argument[1][2] = one;
    plan->call_argument[1][3] = derived_clip_word;
    plan->call_argument[1][4] = one;
    plan->call_argument[1][5] = one;
    plan->call_argument[1][6] = geometry_base;

    plan->call_argument[2][0] = 0xc2040000U;
    plan->call_argument[2][1] = 0x43310000U;
    plan->call_argument[2][2] = one;
    plan->call_argument[2][3] = 0xc2040000U;
    plan->call_argument[2][4] = 0x431f0000U;
    plan->call_argument[2][5] = one;
    plan->call_argument[2][6] = geometry_base;

    plan->call_argument[3][0] = fourth_call_g0;
    plan->call_argument[3][1] = 0x43310000U;
    plan->call_argument[3][2] = one;
    plan->call_argument[3][3] = fourth_call_g0;
    plan->call_argument[3][4] = 0x431f0000U;
    plan->call_argument[3][5] = one;
    plan->call_argument[3][6] = geometry_base;
}
