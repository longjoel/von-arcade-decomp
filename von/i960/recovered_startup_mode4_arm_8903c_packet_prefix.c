/* Selector-2 packet prefix recovered from i960 0x8903c-0x89178. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 record_184;
    recovered_u32 record_8;
    recovered_u32 record_10;
    recovered_u32 table_word_10;
    recovered_u32 table_word_18;
    recovered_u32 first_fifo_response;
    recovered_u32 second_fifo_response;
    recovered_u32 transformed_record_184;
    recovered_u32 derived_first_word;
    recovered_u32 derived_difference;
    recovered_u32 packet_29[3];
    recovered_u32 packet_30[3];
    recovered_u32 packet_31[7];
    recovered_u32 fifo_address;
    recovered_u32 float_constant;
    recovered_u32 first_command;
    recovered_u32 second_command;
    recovered_u32 third_command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8903c_packet_prefix_result;

recovered_startup_mode4_arm_8903c_packet_prefix_result
recovered_startup_mode4_arm_8903c_packet_prefix(
    recovered_u32 record_184, recovered_u32 record_8, recovered_u32 record_10,
    recovered_u32 table_word_10, recovered_u32 table_word_18,
    recovered_u32 first_fifo_response, recovered_u32 second_fifo_response)
{
    recovered_startup_mode4_arm_8903c_packet_prefix_result result;

    result.record_184 = record_184;
    result.record_8 = record_8;
    result.record_10 = record_10;
    result.table_word_10 = table_word_10;
    result.table_word_18 = table_word_18;
    result.first_fifo_response = first_fifo_response;
    result.second_fifo_response = second_fifo_response;
    result.transformed_record_184 = (record_184 - 0x6000U) & 0xffffU;
    result.derived_first_word = first_fifo_response + record_8;
    result.derived_difference = record_10 - second_fifo_response;
    result.packet_29[0] = 29U;
    result.packet_29[1] = result.transformed_record_184;
    result.packet_29[2] = 0x42a00000U;
    result.packet_30[0] = 30U;
    result.packet_30[1] = result.transformed_record_184;
    result.packet_30[2] = 0x42a00000U;
    result.packet_31[0] = 31U;
    result.packet_31[1] = result.derived_first_word;
    result.packet_31[2] = table_word_10;
    result.packet_31[3] = 0U;
    result.packet_31[4] = 0U;
    result.packet_31[5] = result.derived_difference;
    result.packet_31[6] = table_word_18;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.float_constant = 0x42a00000U;
    result.first_command = 29U;
    result.second_command = 30U;
    result.third_command = 31U;
    result.continuation = 0x00089178U;
    return result;
}
