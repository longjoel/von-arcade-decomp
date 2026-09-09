/* Fixed geometry packet path recovered from i960 0xbf2f0-0xbf3dc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 object_byte_0;
    recovered_u32 object_halfword_4;
    recovered_u32 mode_503a08;
    recovered_u32 readback_802008;
} recovered_geometry_constant_packet_input_bf2f0;

typedef struct {
    recovered_u32 accepted;
    recovered_u32 fifo_word[8];
    recovered_u32 fifo_count;
    recovered_u32 control_address;
    recovered_u32 control_value;
    recovered_u32 window_address[4];
    recovered_u32 window_word[4];
    recovered_u32 completion_word;
    recovered_u32 publication_address;
    recovered_u32 publication_value;
} recovered_geometry_constant_packet_plan_bf2f0;

void recovered_geometry_constant_packet_bf2f0(
    const recovered_geometry_constant_packet_input_bf2f0 *input,
    const recovered_u32 table_c4f40[256],
    recovered_geometry_constant_packet_plan_bf2f0 *plan)
{
    recovered_u32 object_byte = input->object_byte_0 & 0xffU;
    recovered_u32 object_halfword = input->object_halfword_4 & 0xffffU;
    recovered_u32 table_value = table_c4f40[object_byte];

    plan->accepted = 0U;
    plan->fifo_count = 0U;
    if (input->mode_503a08 != 2U)
        return;
    if (object_halfword != table_value &&
        object_halfword != (table_value - 1U))
        return;

    plan->accepted = 1U;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 16U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = 0U;
    plan->fifo_word[4] = 0U;
    plan->fifo_word[5] = 0x3f800000U;
    plan->fifo_word[6] = 58U;
    plan->fifo_word[7] = input->readback_802008;
    plan->fifo_count = 8U;
    plan->control_address = 0x00800010U;
    plan->control_value = 0x101U;
    plan->window_address[0] = 0x00804000U;
    plan->window_address[1] = 0x00804004U;
    plan->window_address[2] = 0x00804008U;
    plan->window_address[3] = 0x0080400cU;
    plan->window_word[0] = 0U;
    plan->window_word[1] = 0x0040005cU;
    plan->window_word[2] = 0x008f31a0U;
    plan->window_word[3] = 0U;
    plan->completion_word = 6U;
    plan->publication_address = 0x00801008U;
    plan->publication_value = input->readback_802008 + 0x34U;
}
