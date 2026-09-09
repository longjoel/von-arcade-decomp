/* Event setup-helper opcode-31 packet recovered from i960 0xeaaf0-eab48. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 fifo_response;
    recovered_u32 auxiliary_word;
    recovered_u32 packet[7];
    recovered_u32 packet_count;
    recovered_u32 fifo_address;
    recovered_u32 auxiliary_address;
    recovered_u32 left_word_8_address;
    recovered_u32 right_word_8_address;
    recovered_u32 left_word_10_address;
    recovered_u32 right_word_10_address;
    recovered_u32 opcode;
    recovered_u32 next_target;
} recovered_geometry_event_setup_packet_result_eaaf0;

recovered_geometry_event_setup_packet_result_eaaf0
recovered_geometry_event_setup_packet_eaaf0(recovered_u32 fifo_response,
                                             recovered_u32 auxiliary_word)
{
    recovered_geometry_event_setup_packet_result_eaaf0 result;

    result.fifo_response = fifo_response;
    result.auxiliary_word = auxiliary_word;
    result.packet[0] = 31U;
    result.packet[1] = 0x00503ad8U;
    result.packet[2] = 0x005040d8U;
    result.packet[3] = 0U;
    result.packet[4] = 0U;
    result.packet[5] = 0x00503ae0U;
    result.packet[6] = 0x005040e0U;
    result.packet_count = 7U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.auxiliary_address = 0x00503adcU;
    result.left_word_8_address = 0x00503ad8U;
    result.right_word_8_address = 0x005040d8U;
    result.left_word_10_address = 0x00503ae0U;
    result.right_word_10_address = 0x005040e0U;
    result.opcode = 31U;
    result.next_target = 0x000eab48U;
    return result;
}
