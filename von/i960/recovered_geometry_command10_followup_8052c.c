/* Follow-up command-10 packet and bit gate recovered at 0x8052c-0x805a8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_command10_followup_8052c_plan {
    int32_t selected_word_18;
    int32_t selected_word_10;
    int32_t selected_word_8;
    int32_t object_word_10;
    int32_t object_word_8;
    u32 command10_payload_0;
    u32 command10_payload_1;
    u32 board_response;
    u32 response_minus_selected_word_8;
    u32 bit15_set;
    u32 packet_words;
    u32 fifo_destination;
    u32 clear_bit15_target;
    u32 set_bit15_target;
};

/*
 * The 0x8052c arm computes selected(+0x18)-object(+0x10) and
 * object(+0x08)-selected(+0x10), emits [10, payload0, payload1], reads the
 * response, and branches on bit 15 of response-selected(+0x08).
 */
void recovered_geometry_command10_followup_8052c(
    int32_t selected_word_18,
    int32_t selected_word_10,
    int32_t selected_word_8,
    int32_t object_word_10,
    int32_t object_word_8,
    u32 board_response,
    struct recovered_geometry_command10_followup_8052c_plan *plan)
{
    const int64_t payload_0 = (int64_t)selected_word_18 - object_word_10;
    const int64_t payload_1 = (int64_t)object_word_8 - selected_word_10;
    const int32_t loaded_selected_word_8 =
        (int32_t)(int16_t)((u32)selected_word_8 & 0xffffU);
    const u32 response_difference =
        (u32)((int64_t)(int32_t)board_response - loaded_selected_word_8);

    plan->selected_word_18 = selected_word_18;
    plan->selected_word_10 = selected_word_10;
    plan->selected_word_8 = loaded_selected_word_8;
    plan->object_word_10 = object_word_10;
    plan->object_word_8 = object_word_8;
    plan->command10_payload_0 = (u32)(int32_t)payload_0;
    plan->command10_payload_1 = (u32)(int32_t)payload_1;
    plan->board_response = board_response;
    plan->response_minus_selected_word_8 = response_difference;
    plan->bit15_set = (response_difference >> 15U) & 1U;
    plan->packet_words = 3U;
    plan->fifo_destination = 0x00884000U;
    plan->clear_bit15_target = 0x00080580U;
    plan->set_bit15_target = 0x000805a8U;
}
