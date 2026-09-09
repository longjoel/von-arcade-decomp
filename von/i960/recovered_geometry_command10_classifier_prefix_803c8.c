/* Command-10 packet and classifier-input prefix recovered at 0x803c8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_command10_classifier_prefix_803c8_plan {
    int32_t selected_word_18;
    int32_t selected_word_10;
    int32_t object_word_10;
    int32_t object_word_8;
    int32_t object_word_184;
    u32 command10_payload_0;
    u32 command10_payload_1;
    u32 command10_response;
    u32 classifier_raw_difference;
    int32_t classifier_input;
    u32 packet_words;
    u32 fifo_destination;
    u32 classifier_target;
};

static int32_t normalize_low_halfword(int32_t value)
{
    const u32 low = (u32)value & 0xffffU;
    return (int32_t)((low & 0x8000U) != 0U ? low | 0xffff0000U : low);
}

/*
 * At 0x803b0-0x803c4 the routine forms selected_18-object_10 and
 * object_8-selected_10.  It emits [10, difference0, difference1], consumes
 * the board reply, and at 0x803ec-0x803fc passes the signed low halfword of
 * (reply-object_184) to classifier 0x73508.
 */
void recovered_geometry_command10_classifier_prefix_803c8(
    int32_t selected_word_18,
    int32_t selected_word_10,
    int32_t object_word_10,
    int32_t object_word_8,
    int32_t object_word_184,
    u32 command10_response,
    struct recovered_geometry_command10_classifier_prefix_803c8_plan *plan)
{
    const int64_t payload_0 = (int64_t)selected_word_18 - object_word_10;
    const int64_t payload_1 = (int64_t)object_word_8 - selected_word_10;
    const int32_t loaded_object_word_184 =
        (int32_t)(int16_t)((u32)object_word_184 & 0xffffU);
    const int64_t raw_difference =
        (int64_t)(int32_t)command10_response - loaded_object_word_184;

    plan->selected_word_18 = selected_word_18;
    plan->selected_word_10 = selected_word_10;
    plan->object_word_10 = object_word_10;
    plan->object_word_8 = object_word_8;
    plan->object_word_184 = loaded_object_word_184;
    plan->command10_payload_0 = (u32)(int32_t)payload_0;
    plan->command10_payload_1 = (u32)(int32_t)payload_1;
    plan->command10_response = command10_response;
    plan->classifier_raw_difference = (u32)(int32_t)raw_difference;
    plan->classifier_input = normalize_low_halfword((int32_t)raw_difference);
    plan->packet_words = 3U;
    plan->fifo_destination = 0x00884000U;
    plan->classifier_target = 0x00073508U;
}
