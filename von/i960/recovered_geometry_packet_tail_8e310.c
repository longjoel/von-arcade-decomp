/* Pure byte-indexed geometry packet tail recovered from i960 0x8e310-0x8e398. */
#include "recovered_common.h"
struct recovered_geometry_packet_tail_8e310_input {
    recovered_u32 vector_1, vector_3, vector_5;
    recovered_u32 byte_m2, byte_m1, byte_0;
    recovered_u32 frame_readback;
};
struct recovered_geometry_packet_tail_8e310_plan {
    recovered_u32 fifo_word[10], fifo_count;
};
void recovered_geometry_packet_tail_8e310(const struct recovered_geometry_packet_tail_8e310_input *i, struct recovered_geometry_packet_tail_8e310_plan *p)
{
    p->fifo_word[0]=5U;
    p->fifo_word[1]=i->vector_1&0xffffU;
    p->fifo_word[2]=i->vector_3&0xffffU;
    p->fifo_word[3]=i->vector_5&0xffffU;
    p->fifo_word[4]=46U; /* 31 + 15 */
    p->fifo_word[5]=i->byte_m2&0xffU;
    p->fifo_word[6]=i->byte_m1&0xffU;
    p->fifo_word[7]=i->byte_0&0xffU;
    p->fifo_word[8]=0x1fU;
    p->fifo_word[9]=i->frame_readback;
    p->fifo_count=10U;
}
