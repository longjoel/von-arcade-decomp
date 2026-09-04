/* Clear-flag geometry packet recovered from i960 0x9d454-0x9d59c. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

/* Reference form of the extended-FP sequence at 0x9d454. The two constants
 * are exact binary values; the final cast models the single-precision word
 * written to the geometry FIFO. The packet builder still accepts an explicit
 * result because host double is not the i960 extended format. */
u32 recovered_geometry_clear_flag_derived_word(int16_t object_1e4)
{
    union {
        float value;
        u32 bits;
    } result;
    double quotient = (double)object_1e4 / 3.390625;

    result.value = (float)(quotient * 3.0625);
    return result.bits;
}

struct recovered_geometry_clear_flag_packet_plan {
    int16_t object_1e4;
    u32 derived_packet_word;
    u32 fifo_address;
    u32 fifo_word_count;
    u32 fifo_word[9];
    u32 board_readback_address;
    u32 published_pointer_address;
    u32 published_pointer_offset;
    u32 object_flag_1de;
    u32 frame_value;
    u32 control_address;
    u32 control_value;
    u32 frame_publish_address;
    u32 frame_word[2];
    u32 frame_tail[2];
    u32 frame_variant;
};

void recovered_geometry_clear_flag_packet_plan(
    int16_t object_1e4, u32 derived_packet_word, u32 object_flag_1de,
    u32 frame_value, u32 board_readback_address,
    struct recovered_geometry_clear_flag_packet_plan *plan)
{
    plan->object_1e4 = object_1e4;
    plan->derived_packet_word = derived_packet_word;
    plan->fifo_address = RECOVERED_FIFO_ADDRESS;
    plan->fifo_word_count = 9U;
    recovered_fill_nine_word_geometry_packet(plan->fifo_word, derived_packet_word);
    plan->board_readback_address = board_readback_address;
    plan->published_pointer_address = RECOVERED_FRAME_POINTER;
    plan->published_pointer_offset = RECOVERED_POINTER_OFFSET;
    plan->object_flag_1de = object_flag_1de & 0xffU;
    plan->frame_value = frame_value;
    plan->control_address = RECOVERED_GEOMETRY_CONTROL;
    plan->control_value = RECOVERED_GEOMETRY_CONTROL_VALUE;
    plan->frame_publish_address = RECOVERED_FRAME_PUBLISH;
    plan->frame_tail[0] = RECOVERED_FRAME_CONSTANT;
    plan->frame_tail[1] = 1U;

    if (plan->object_flag_1de == 0U) {
        plan->frame_variant = 0U;
        plan->frame_word[0] = 0U;
        plan->frame_word[1] = 0x40005cU;
    } else {
        plan->frame_variant = 1U;
        plan->frame_word[0] = frame_value;
        plan->frame_word[1] = 0x40002cU;
    }
}
