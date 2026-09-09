/* Indexed table packet callsite from i960 0x9225c-0x92380. */
#include "recovered_common.h"

struct recovered_geometry_table_packet_callsite_9225c_plan {
    recovered_u32 source_value;
    recovered_u32 remainder;
    recovered_u32 frame_word;
    recovered_u32 frame_readback;
    recovered_u32 fifo_word[14];
    recovered_u32 fifo_count;
    recovered_u32 table_base;
    recovered_u32 table_index;
    recovered_u32 response_word[3];
    recovered_u32 control_address;
    recovered_u32 control_value;
    recovered_u32 publish_address;
    recovered_u32 published;
    recovered_u32 completion_word;
};

void recovered_geometry_table_packet_callsite_9225c(
    recovered_u32 source_value, recovered_u32 frame_word,
    recovered_u32 frame_readback, const recovered_u32 response_word[3],
    struct recovered_geometry_table_packet_callsite_9225c_plan *plan)
{
    recovered_u32 remainder = source_value % 30U;

    plan->source_value = source_value;
    plan->remainder = remainder;
    plan->frame_word = frame_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = remainder;
    plan->fifo_word[3] = 0x40e00000U;
    plan->fifo_word[4] = 0x41800000U;
    plan->fifo_word[5] = frame_word;
    plan->fifo_word[6] = 21U;
    plan->fifo_word[7] = 0xb800U;
    plan->fifo_word[8] = 19U;
    plan->fifo_word[9] = 0x40400000U;
    plan->fifo_word[10] = 0x40400000U;
    plan->fifo_word[11] = 0x40400000U;
    plan->fifo_word[12] = 58U;
    plan->fifo_word[13] = frame_readback;
    plan->fifo_count = 14U;
    plan->table_base = 0x2be52b0U;
    plan->table_index = remainder * 12U;
    for (unsigned i = 0; i < 3; ++i)
        plan->response_word[i] = response_word[i];
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->published = response_word[0] != 0U ? 1U : 0U;
    plan->completion_word = 6U;
}
