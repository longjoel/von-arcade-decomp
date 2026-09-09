/* Selector-0 floating/packet tail recovered from i960 0x8aa54-0x8aba4. */
#include "recovered_common.h"

typedef union {
    recovered_u32 bits;
    float value;
} recovered_float_bits;

typedef struct {
    recovered_u32 helper_result;
    recovered_u32 selected_float;
    recovered_u32 adjusted_float;
    recovered_u32 timing_5770f0;
    recovered_u32 first_packet_word_1;
    recovered_u32 first_packet_word_2;
    recovered_u32 second_response;
    recovered_u32 computed_float_word;
    recovered_u32 first_response;
    recovered_u32 record_30;
    recovered_u32 command_10_packet_0[3];
    recovered_u32 command_10_packet_1[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 state_51c94c;
    recovered_u32 fifo_address;
    recovered_u32 command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8aa54_float_packet_tail_result;

recovered_startup_mode4_arm_8aa54_float_packet_tail_result
recovered_startup_mode4_arm_8aa54_float_packet_tail(
    recovered_u32 helper_result, recovered_u32 timing_5770f0,
    recovered_u32 first_packet_word_1, recovered_u32 first_packet_word_2,
    recovered_u32 second_response, recovered_u32 computed_float_word,
    recovered_u32 first_response, recovered_u32 record_30,
    recovered_u32 state_51c948)
{
    recovered_startup_mode4_arm_8aa54_float_packet_tail_result result;
    recovered_float_bits helper;
    recovered_float_bits selected;

    helper.bits = helper_result;
    result.helper_result = helper_result;
    result.selected_float = helper.value <= 0.0F ? helper_result : 0x41f00000U;
    selected.bits = result.selected_float;
    result.adjusted_float = selected.bits;
    if (timing_5770f0 == 0U) {
        selected.value += 2.5F;
        result.adjusted_float = selected.bits;
    }
    result.timing_5770f0 = timing_5770f0;
    result.first_packet_word_1 = first_packet_word_1;
    result.first_packet_word_2 = first_packet_word_2;
    result.second_response = second_response;
    result.computed_float_word = computed_float_word;
    result.first_response = first_response;
    result.record_30 = record_30;
    result.command_10_packet_0[0] = 10U;
    result.command_10_packet_0[1] = first_packet_word_1;
    result.command_10_packet_0[2] = first_packet_word_2;
    result.command_10_packet_1[0] = 10U;
    result.command_10_packet_1[1] = state_51c948;
    result.command_10_packet_1[2] = computed_float_word;
    result.state_51c940 = first_response;
    result.state_51c944 = second_response;
    result.state_51c94c = computed_float_word;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command = 10U;
    result.continuation = record_30 == 0U ? 0x0008b604U : 0x0008aeccU;
    return result;
}
