/* Third clear-flag geometry packet recovered from i960 0x9dc64-0x9ddac. */
#include <stdint.h>

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
    plan->fifo_address = 0x00884000U;
    plan->fifo_word_count = 9U;
    plan->fifo_word[0] = 19U;
    plan->fifo_word[1] = derived_packet_word;
    plan->fifo_word[2] = 0x40a00000U;
    plan->fifo_word[3] = 0x3f800000U;
    plan->fifo_word[4] = 18U;
    plan->fifo_word[5] = 0x3f800000U;
    plan->fifo_word[6] = 0U;
    plan->fifo_word[7] = 0U;
    plan->fifo_word[8] = 58U;
    plan->board_readback_address = board_readback_address;
    plan->published_pointer_address = 0x00801008U;
    plan->published_pointer_offset = 0x34U;
    plan->object_flag_1df = object_flag_1df & 0xffU;
    plan->frame_value = frame_value;
    plan->control_address = 0x00800010U;
    plan->control_value = 0x101U;
    plan->frame_publish_address = 0x00804000U;
    plan->frame_tail[0] = 0x084553fU;
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
