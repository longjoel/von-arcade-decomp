/* Third clear-flag geometry packet recovered from i960 0x9dc64-0x9ddac. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_geometry_third_clear_flag_packet_plan {
    int16_t object_1e6;
    u32 derived_packet_word;
    u32 fifo_address;
    u32 fifo_word_count;
    u32 fifo_word[9];
    u32 board_readback_address;
    u32 published_pointer_address;
    u32 published_pointer_offset;
    u32 object_flag_1df;
    u32 frame_value;
    u32 control_address;
    u32 control_value;
    u32 frame_publish_address;
    u32 frame_slot_offset;
    u32 frame_word[2];
    u32 frame_tail_offset;
    u32 frame_tail[2];
    u32 frame_variant;
};

void recovered_geometry_third_clear_flag_packet_plan(
    int16_t object_1e6, u32 derived_packet_word, u32 object_flag_1df,
    u32 frame_value, u32 board_readback_address,
    struct recovered_geometry_third_clear_flag_packet_plan *plan)
{
    plan->object_1e6 = object_1e6;
    plan->derived_packet_word = derived_packet_word;
    plan->fifo_address = RECOVERED_FIFO_ADDRESS;
    plan->fifo_word_count = 9U;
    recovered_fill_nine_word_geometry_packet(plan->fifo_word, derived_packet_word);
    plan->board_readback_address = board_readback_address;
    plan->published_pointer_address = RECOVERED_FRAME_POINTER;
    plan->published_pointer_offset = RECOVERED_POINTER_OFFSET;
    plan->object_flag_1df = object_flag_1df & 0xffU;
    plan->frame_value = frame_value;
    plan->control_address = RECOVERED_GEOMETRY_CONTROL;
    plan->control_value = RECOVERED_GEOMETRY_CONTROL_VALUE;
    plan->frame_publish_address = RECOVERED_FRAME_PUBLISH;
    plan->frame_tail[0] = RECOVERED_FRAME_CONSTANT;
    plan->frame_tail[1] = 1U;

    if (plan->object_flag_1df == 0U) {
        plan->frame_variant = 0U;
        plan->frame_slot_offset = 0x80U;
        plan->frame_word[0] = frame_value;
        plan->frame_word[1] = 0x40005cU;
        plan->frame_tail_offset = 0x88U;
    } else {
        plan->frame_variant = 1U;
        plan->frame_slot_offset = 0x90U;
        plan->frame_word[0] = frame_value;
        plan->frame_word[1] = 0x40002cU;
        plan->frame_tail_offset = 0x98U;
    }
}
