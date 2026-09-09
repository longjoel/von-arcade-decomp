/* Object packet common-tail prefix recovered from i960 0xe7454-0xe7490. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 queue_flag;
    recovered_u32 computed_offset;
    recovered_u32 suffix_word_count;
    recovered_u32 suffix_words[5];
    recovered_u32 fifo_address;
    recovered_u32 control_read_address;
    recovered_u32 control_write_address;
    recovered_u32 common_target;
} recovered_geometry_object_packet_tail_result_e7454;

recovered_geometry_object_packet_tail_result_e7454
recovered_geometry_object_packet_tail_e7454(recovered_u32 queue_flag,
                                            recovered_u32 computed_offset)
{
    recovered_geometry_object_packet_tail_result_e7454 result = {
        queue_flag, computed_offset, 0U, {0U, 0U, 0U, 0U, 0U},
        0x00884000U, 0x00802008U, 0x00801008U, 0x000e7490U
    };

    if (queue_flag == 0U) {
        result.suffix_word_count = 5U;
        result.suffix_words[0] = 19U;
        result.suffix_words[1] = 0x3f800000U;
        result.suffix_words[2] = 0x3f800000U;
        result.suffix_words[3] = 0x41200000U;
        result.suffix_words[4] = computed_offset + 27U;
    }
    return result;
}
