/* Third flagged geometry state packet recovered from i960 0x9db3c-0x9dc64. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_third_flagged_state_packet_plan {
    u32 flag_bit1;
    int16_t state_word;
    u32 masked_state_parameter;
    u32 derived_packet_word;
    u32 fifo_address;
    u32 fifo_word_count;
    u32 fifo_word[13];
    u32 board_readback_address;
    u32 published_pointer_address;
    u32 published_pointer_offset;
    u32 control_address;
    u32 control_value;
    u32 frame_publish_address;
    u32 frame_word[2];
    u32 frame_tail[2];
    u32 frame_value;
};

void recovered_geometry_third_flagged_state_packet_plan(
    u32 object_flag_1df, int16_t state_word, u32 derived_packet_word,
    u32 frame_value, u32 board_readback_address,
    struct recovered_geometry_third_flagged_state_packet_plan *plan)
{
    plan->flag_bit1 = (object_flag_1df >> 1) & 1U;
    plan->state_word = state_word;
    plan->masked_state_parameter =
        (((u32)(uint16_t)state_word & 0xfU) << 12) & 0xf000U;
    plan->derived_packet_word = derived_packet_word;
    plan->fifo_address = 0x00884000U;
    plan->fifo_word_count = plan->flag_bit1 ? 13U : 0U;
    plan->board_readback_address = board_readback_address;
    plan->published_pointer_address = 0x00801008U;
    plan->published_pointer_offset = 0x34U;
    plan->control_address = 0x00800010U;
    plan->control_value = 0x101U;
    plan->frame_publish_address = 0x00804000U;
    plan->frame_word[0] = frame_value;
    plan->frame_word[1] = 0x40009cU;
    plan->frame_tail[0] = 0x084553fU;
    plan->frame_tail[1] = 1U;
    plan->frame_value = frame_value;

    if (!plan->flag_bit1)
        return;

    plan->fifo_word[0] = 29U;
    plan->fifo_word[1] = plan->masked_state_parameter;
    plan->fifo_word[2] = 0x40400000U;
    plan->fifo_word[3] = 19U;
    plan->fifo_word[4] = derived_packet_word;
    plan->fifo_word[5] = 0x42200000U;
    plan->fifo_word[6] = derived_packet_word;
    plan->fifo_word[7] = 0x3f800000U;
    plan->fifo_word[8] = 18U;
    plan->fifo_word[9] = 0x3f800000U;
    plan->fifo_word[10] = 0U;
    plan->fifo_word[11] = 0U;
    plan->fifo_word[12] = 58U;
}
