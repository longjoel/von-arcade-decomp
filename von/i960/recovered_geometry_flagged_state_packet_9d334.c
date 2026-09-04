/* Flagged geometry state packet recovered from i960 0x9d334-0x9d454. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_geometry_flagged_state_packet_plan {
    u32 flag_bit1;
    u32 state_word;
    u32 state_low_nibble;
    u32 masked_state_parameter;
    u32 fifo_address;
    u32 fifo_word_count;
    u32 fifo_word[13];
    u32 first_response_address;
    u32 second_response_address;
    u32 published_pointer_address;
    u32 published_pointer_offset;
    u32 control_address;
    u32 control_value;
    u32 frame_publish_address;
    u32 frame_word[2];
    u32 first_board_response;
    u32 second_derived_word;
};

void recovered_geometry_flagged_state_packet_plan(
    u32 object_flag, int16_t state_word, u32 first_board_response,
    u32 second_derived_word,
    struct recovered_geometry_flagged_state_packet_plan *plan)
{
    plan->flag_bit1 = (object_flag >> 1) & 1U;
    plan->state_word = (uint16_t)state_word;
    plan->state_low_nibble = ((u32)(uint16_t)state_word) & 0xfU;
    plan->masked_state_parameter = (plan->state_low_nibble << 12) & 0xf000U;
    plan->fifo_address = RECOVERED_FIFO_ADDRESS;
    plan->first_response_address = 0x00884000U;
    plan->second_response_address = 0x00884000U;
    plan->published_pointer_address = RECOVERED_FRAME_POINTER;
    plan->published_pointer_offset = RECOVERED_POINTER_OFFSET;
    plan->control_address = RECOVERED_GEOMETRY_CONTROL;
    plan->control_value = RECOVERED_GEOMETRY_CONTROL_VALUE;
    plan->frame_publish_address = RECOVERED_FRAME_PUBLISH;
    plan->frame_word[0] = 0U;
    plan->frame_word[1] = 0x40009cU;
    plan->first_board_response = first_board_response;
    plan->second_derived_word = second_derived_word;
    plan->fifo_word_count = plan->flag_bit1 ? 13U : 0U;

    if (!plan->flag_bit1)
        return;

    recovered_fill_thirteen_word_geometry_packet(plan->fifo_word,
                                                  plan->masked_state_parameter,
                                                  second_derived_word);
}
