/* Selector-0 downstream packet/state prefix recovered from i960 0x89c04-0x89cf4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 counter_51c984;
    recovered_u32 prior_fifo_response;
    recovered_u32 computed_packet_word;
    recovered_u32 record_8;
    recovered_u32 record_10;
    recovered_u32 timing_delta;
    recovered_u32 transformed_base;
    recovered_u32 transformed_base_low16;
    recovered_u32 first_fifo_response;
    recovered_u32 second_fifo_response;
    recovered_u32 packet_29[3];
    recovered_u32 packet_30[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c942;
    recovered_u32 state_51c948;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 fifo_address;
    recovered_u32 first_command;
    recovered_u32 second_command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_89c04_packet_state_prefix_result;

recovered_startup_mode4_arm_89c04_packet_state_prefix_result
recovered_startup_mode4_arm_89c04_packet_state_prefix(
    recovered_u32 counter_51c984, recovered_u32 prior_fifo_response,
    recovered_u32 computed_packet_word, recovered_u32 record_8,
    recovered_u32 record_10, recovered_u32 first_fifo_response,
    recovered_u32 second_fifo_response)
{
    recovered_startup_mode4_arm_89c04_packet_state_prefix_result result;

    result.counter_51c984 = counter_51c984;
    result.prior_fifo_response = prior_fifo_response;
    result.computed_packet_word = computed_packet_word;
    result.record_8 = record_8;
    result.record_10 = record_10;
    result.timing_delta = 0xb4U - counter_51c984;
    result.transformed_base = prior_fifo_response + 0x1000U -
        (result.timing_delta << 8U);
    result.transformed_base_low16 = result.transformed_base & 0xffffU;
    result.first_fifo_response = first_fifo_response;
    result.second_fifo_response = second_fifo_response;
    result.packet_29[0] = 29U;
    result.packet_29[1] = result.transformed_base_low16;
    result.packet_29[2] = computed_packet_word;
    result.packet_30[0] = 30U;
    result.packet_30[1] = result.transformed_base_low16;
    result.packet_30[2] = computed_packet_word;
    result.state_51c940 = result.transformed_base;
    result.state_51c942 = result.timing_delta;
    result.state_51c948 = computed_packet_word;
    result.state_51c950 = first_fifo_response + record_8;
    result.state_51c954 = record_10 - second_fifo_response;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.first_command = 29U;
    result.second_command = 30U;
    result.continuation = 0x00089cf4U;
    return result;
}
