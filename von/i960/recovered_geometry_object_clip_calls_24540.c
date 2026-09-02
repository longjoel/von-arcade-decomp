/* Object command-6 clip calls recovered from i960 0x24540-0x2468c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_object_clip_calls_plan {
    u32 clip_dispatch;
    u32 selected_pointer;
    u32 frame_selected_offset;
    u32 frame_pointer_offset;
    u32 frame_constants[2];
    u32 control_address;
    u32 control_value;
    u32 frame_publish_address;
    u32 frame_pointer_address;
    u32 fifo_address;
    u32 call_count;
    u32 call_argument[4][7];
};

void recovered_geometry_object_clip_calls_plan(
    u32 selected_pointer, u32 derived_call_value,
    struct recovered_geometry_object_clip_calls_plan *plan)
{
    static const u32 one = 0x3f800000U;
    static const u32 geometry_base = 0x400028U;

    plan->clip_dispatch = 0x000701a0U;
    plan->selected_pointer = selected_pointer;
    plan->frame_selected_offset = 0x50U;
    plan->frame_pointer_offset = 0x54U;
    plan->frame_constants[0] = 0x084553fU;
    plan->frame_constants[1] = 1U;
    plan->control_address = 0x00800010U;
    plan->control_value = 0x101U;
    plan->frame_publish_address = 0x00804000U;
    plan->frame_pointer_address = 0x00804004U;
    plan->fifo_address = 0x00884000U;
    plan->call_count = 4U;

    plan->call_argument[0][0] = 0xc2040000U;
    plan->call_argument[0][1] = 0x431c0000U;
    plan->call_argument[0][2] = one;
    plan->call_argument[0][3] = 0xc2040000U;
    plan->call_argument[0][4] = 0x43130000U;
    plan->call_argument[0][5] = one;
    plan->call_argument[0][6] = geometry_base;

    plan->call_argument[1][0] = derived_call_value;
    plan->call_argument[1][1] = 0x431c0000U;
    plan->call_argument[1][2] = one;
    plan->call_argument[1][3] = derived_call_value;
    plan->call_argument[1][4] = 0x43130000U;
    plan->call_argument[1][5] = one;
    plan->call_argument[1][6] = geometry_base;

    plan->call_argument[2][0] = 0xc2040000U;
    plan->call_argument[2][1] = 0x43130000U;
    plan->call_argument[2][2] = one;
    plan->call_argument[2][3] = derived_call_value;
    plan->call_argument[2][4] = 0x43130000U;
    plan->call_argument[2][5] = one;
    plan->call_argument[2][6] = geometry_base;

    plan->call_argument[3][0] = 0xc2040000U;
    plan->call_argument[3][1] = 0x431c0000U;
    plan->call_argument[3][2] = one;
    plan->call_argument[3][3] = derived_call_value;
    plan->call_argument[3][4] = 0x431c0000U;
    plan->call_argument[3][5] = one;
    plan->call_argument[3][6] = geometry_base;

}
