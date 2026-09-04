/* Common mode-zero geometry sequence recovered from i960 0x24cc8-0x24eb0. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_geometry_mode_zero_clip_calls_plan {
    u32 fifo_address;
    u32 fifo_prefix_count;
    u32 fifo_prefix[15];
    u32 frame_pointer;
    u32 frame_pointer_offset;
    u32 frame_constant_address;
    u32 frame_constant;
    u32 frame_flag_offset;
    u32 frame_flag;
    u32 board_readback_address;
    u32 control_address;
    u32 control_value;
    u32 frame_publish_address;
    u32 clip_dispatch;
    u32 call_count;
    u32 call_argument[4][7];
};

void recovered_geometry_mode_zero_clip_calls_plan(
    u32 frame_pointer, u32 board_readback_address,
    struct recovered_geometry_mode_zero_clip_calls_plan *plan)
{
    static const u32 one = RECOVERED_FLOAT_ONE;
    static const u32 geometry_base = 0x400028U;

    plan->fifo_address = RECOVERED_FIFO_ADDRESS;
    plan->fifo_prefix_count = 15U;
    plan->fifo_prefix[0] = 5U;
    plan->fifo_prefix[1] = 16U;
    plan->fifo_prefix[2] = 18U;
    plan->fifo_prefix[3] = 0xbe8f5c29U;
    plan->fifo_prefix[4] = 0x3e8bf259U;
    plan->fifo_prefix[5] = one;
    plan->fifo_prefix[6] = 19U;
    plan->fifo_prefix[7] = 0x3ada740eU;
    plan->fifo_prefix[8] = 0x3ada740eU;
    plan->fifo_prefix[9] = one;
    plan->fifo_prefix[10] = 19U;
    plan->fifo_prefix[11] = 0x428c0000U;
    plan->fifo_prefix[12] = 0x41400000U;
    plan->fifo_prefix[13] = one;
    plan->fifo_prefix[14] = 58U;

    plan->frame_pointer = frame_pointer;
    plan->frame_pointer_offset = 0xb0U;
    plan->frame_constant_address = 0x40000cU;
    plan->frame_constant = 0x084553fU;
    plan->frame_flag_offset = 0xbcU;
    plan->frame_flag = 1U;
    plan->board_readback_address = board_readback_address;
    plan->control_address = RECOVERED_GEOMETRY_CONTROL;
    plan->control_value = RECOVERED_GEOMETRY_CONTROL_VALUE;
    plan->frame_publish_address = RECOVERED_FRAME_PUBLISH;
    plan->clip_dispatch = 0x000701a0U;
    plan->call_count = 4U;

    plan->call_argument[0][0] = 0xc2c40000U;
    plan->call_argument[0][1] = 0x432f0000U;
    plan->call_argument[0][2] = one;
    plan->call_argument[0][3] = 0xc36f0000U;
    plan->call_argument[0][4] = 0x432f0000U;
    plan->call_argument[0][5] = one;
    plan->call_argument[0][6] = geometry_base;

    plan->call_argument[1][0] = 0xc36f0000U;
    plan->call_argument[1][1] = 0x43170000U;
    plan->call_argument[1][2] = one;
    plan->call_argument[1][3] = 0xc2c40000U;
    plan->call_argument[1][4] = 0x43170000U;
    plan->call_argument[1][5] = one;
    plan->call_argument[1][6] = geometry_base;

    plan->call_argument[2][0] = 0xc36f0000U;
    plan->call_argument[2][1] = 0x432f0000U;
    plan->call_argument[2][2] = one;
    plan->call_argument[2][3] = 0xc36f0000U;
    plan->call_argument[2][4] = 0x43170000U;
    plan->call_argument[2][5] = one;
    plan->call_argument[2][6] = geometry_base;

    plan->call_argument[3][0] = 0xc2c40000U;
    plan->call_argument[3][1] = 0x43170000U;
    plan->call_argument[3][2] = one;
    plan->call_argument[3][3] = 0xc36f0000U;
    plan->call_argument[3][4] = 0x432f0000U;
    plan->call_argument[3][5] = one;
    plan->call_argument[3][6] = geometry_base;
}
