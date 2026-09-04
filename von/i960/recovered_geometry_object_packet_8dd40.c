/* Pure object-state packet contract recovered from i960 0x8dd40-0x8dfb0. */
#include "recovered_common.h"

struct recovered_geometry_object_packet_8dd40_input {
    recovered_u32 coordinate_m2;
    recovered_u32 coordinate_0;
    recovered_u32 coordinate_2;
    recovered_u32 coordinate_4;
    recovered_u32 coordinate_6;
    recovered_u32 coordinate_8;
    recovered_u32 coordinate_10;
    recovered_u32 fifo_read_value;
    recovered_u32 object_word;
    recovered_u32 selected_word4;
    recovered_u32 selected_word8;
    recovered_u32 object_word_c;
    recovered_u32 output_low;
    recovered_u32 output_high;
    recovered_u32 frame_readback;
    recovered_u32 table_index;
};

struct recovered_geometry_object_packet_8dd40_plan {
    recovered_u32 fifo_word[13];
    recovered_u32 fifo_count;
    recovered_u32 fifo_read_address;
    recovered_u32 fifo_read_value;
    recovered_u32 control_address;
    recovered_u32 control_value;
    recovered_u32 window_address[4];
    recovered_u32 window_word[4];
    recovered_u32 completion_word;
    recovered_u32 selected_field_offset;
    recovered_u32 selected_field_value;
    recovered_u32 output_address_low;
    recovered_u32 output_address_high;
    recovered_u32 output_low;
    recovered_u32 output_high;
    recovered_u32 table_write;
    recovered_u32 table_address;
};

void recovered_geometry_object_packet_8dd40(
    const struct recovered_geometry_object_packet_8dd40_input *input,
    struct recovered_geometry_object_packet_8dd40_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 47U;
    plan->fifo_word[2] = input->coordinate_6 & 0xffffU;
    plan->fifo_word[3] = input->coordinate_8 & 0xffffU;
    plan->fifo_word[4] = input->coordinate_10 & 0xffffU;
    plan->fifo_word[5] = 22U;
    plan->fifo_word[6] = input->coordinate_4 & 0xffffU;
    plan->fifo_word[7] = 21U;
    plan->fifo_word[8] = input->coordinate_2 & 0xffffU;
    plan->fifo_word[9] = 20U;
    plan->fifo_word[10] = input->coordinate_0 & 0xffffU;
    plan->fifo_word[11] = 58U;
    plan->fifo_word[12] = input->frame_readback;
    plan->fifo_count = 13U;
    plan->fifo_read_address = 0x00884000U;
    plan->fifo_read_value = input->fifo_read_value;
    plan->control_address = 0x00800010U;
    plan->control_value = 0x101U;
    plan->window_address[0] = 0x00804000U;
    plan->window_address[1] = 0x00804004U;
    plan->window_address[2] = 0x00804008U;
    plan->window_address[3] = 0x0080400cU;
    plan->window_word[0] = input->object_word;
    plan->window_word[1] = input->fifo_read_value ? input->selected_word8 : input->selected_word4;
    plan->window_word[2] = input->object_word_c;
    plan->window_word[3] = 0U;
    plan->completion_word = 6U;
    plan->selected_field_offset = input->fifo_read_value ? 8U : 4U;
    plan->selected_field_value = input->fifo_read_value ? input->selected_word8 : input->selected_word4;
    plan->output_address_low = 0x174U;
    plan->output_address_high = 0x17cU;
    plan->output_low = input->output_low;
    plan->output_high = input->output_high;
    plan->table_write = (input->table_index < 5U);
    plan->table_address = 0x562430U + input->table_index * 12U;
}
