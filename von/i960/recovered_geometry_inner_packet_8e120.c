/* Pure per-record contract for i960 0x8e120-0x8e2b0. */
#include "recovered_common.h"
struct recovered_geometry_inner_packet_8e120_input {
    recovered_u32 value_m2, value_0, value_2, value_4, value_6, value_8;
    recovered_u32 parameter;
    recovered_u32 object_word, object_field4, object_field8, object_word_c;
    recovered_u32 fifo_response, frame_readback, returned_low, returned_high;
    recovered_u32 direct_destination, table_index;
};
struct recovered_geometry_inner_packet_8e120_plan {
    recovered_u32 fifo_word[13], fifo_count;
    recovered_u32 selected_offset, selected_value;
    recovered_u32 control_address, control_value, window_address[4], window_word[4];
    recovered_u32 completion_word, fifo_read_address, fifo_read_value;
    recovered_u32 low_address, high_address, low_value, high_value;
    recovered_u32 table_write, table_address;
};
void recovered_geometry_inner_packet_8e120(const struct recovered_geometry_inner_packet_8e120_input *i, struct recovered_geometry_inner_packet_8e120_plan *p)
{
    p->fifo_word[0]=5U; p->fifo_word[1]=47U;
    p->fifo_word[2]=i->value_m2&0xffffU; p->fifo_word[3]=i->value_0&0xffffU; p->fifo_word[4]=i->value_2&0xffffU;
    p->fifo_word[5]=22U; p->fifo_word[6]=i->value_4&0xffffU;
    p->fifo_word[7]=21U; p->fifo_word[8]=i->value_6&0xffffU;
    p->fifo_word[9]=20U; p->fifo_word[10]=i->parameter&0xffffU; p->fifo_word[11]=58U; p->fifo_word[12]=i->frame_readback; p->fifo_count=13U;
    p->fifo_read_address=0x884000U; p->fifo_read_value=i->fifo_response;
    p->selected_offset=i->fifo_response?8U:4U; p->selected_value=i->fifo_response?i->object_field8:i->object_field4;
    p->control_address=0x800010U; p->control_value=0x101U;
    p->window_address[0]=0x804000U; p->window_address[1]=0x804004U; p->window_address[2]=0x804008U; p->window_address[3]=0x80400cU;
    p->window_word[0]=i->object_word; p->window_word[1]=p->selected_value; p->window_word[2]=i->object_word_c; p->window_word[3]=0U; p->completion_word=6U;
    p->low_value=i->returned_low; p->high_value=i->returned_high;
    p->table_write=!i->direct_destination && i->table_index<5U;
    p->table_address=0x562430U+i->table_index*12U;
    p->low_address=i->direct_destination?0x174U:p->table_address;
    p->high_address=i->direct_destination?0x17cU:p->table_address+8U;
}
