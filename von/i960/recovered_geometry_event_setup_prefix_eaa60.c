/* Event setup-helper prefix recovered from i960 0xeaa60-eaaec. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 left_word_8;
    recovered_u32 left_word_10;
    recovered_u32 right_word_8;
    recovered_u32 right_word_10;
    recovered_u32 setup_packet[2];
    recovered_u32 delta_packet[3];
    recovered_u32 setup_packet_count;
    recovered_u32 delta_packet_count;
    recovered_u32 init_helper;
    recovered_u32 frame_setup_helper;
    recovered_u32 frame_setup_argument;
    recovered_u32 fifo_address;
    recovered_u32 left_record_base;
    recovered_u32 right_record_base;
    recovered_u32 delta_word_10;
    recovered_u32 delta_word_8;
    recovered_u32 next_target;
} recovered_geometry_event_setup_prefix_result_eaa60;

recovered_geometry_event_setup_prefix_result_eaa60
recovered_geometry_event_setup_prefix_eaa60(
    recovered_u32 left_word_8, recovered_u32 left_word_10,
    recovered_u32 right_word_8, recovered_u32 right_word_10)
{
    recovered_geometry_event_setup_prefix_result_eaa60 result;

    result.left_word_8 = left_word_8;
    result.left_word_10 = left_word_10;
    result.right_word_8 = right_word_8;
    result.right_word_10 = right_word_10;
    result.setup_packet[0] = 8U;
    result.setup_packet[1] = 16U;
    result.delta_word_10 = right_word_10 - left_word_10;
    result.delta_word_8 = right_word_8 - left_word_8;
    result.delta_packet[0] = 10U;
    result.delta_packet[1] = result.delta_word_10;
    result.delta_packet[2] = result.delta_word_8;
    result.setup_packet_count = 2U;
    result.delta_packet_count = 3U;
    result.init_helper = 0x000295d0U;
    result.frame_setup_helper = 0x0002a990U;
    result.frame_setup_argument = 0x0000d000U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.left_record_base = 0x00503ad8U;
    result.right_record_base = 0x005040d8U;
    result.next_target = 0x000eaaf0U;
    return result;
}
