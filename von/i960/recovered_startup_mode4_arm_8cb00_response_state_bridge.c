/* Response-helper state bridge recovered from i960 0x8cb00-0x8cc0c. */
#include "recovered_common.h"

typedef union {
    recovered_u32 bits;
    float value;
} recovered_float_bits;

typedef struct {
    recovered_u32 first_fifo_response;
    recovered_u32 second_fifo_response;
    recovered_u32 current_record_8;
    recovered_u32 current_record_10;
    recovered_u32 state_51c940;
    recovered_u32 state_51c948;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 timing_5770f0;
    recovered_u32 adjusted_timing;
    recovered_u32 helper_result;
    recovered_u32 selected_float;
    recovered_u32 timing_zero_path;
    recovered_u32 command_29_packet[3];
    recovered_u32 command_30_packet[3];
    recovered_u32 helper_input_x;
    recovered_u32 helper_input_y;
    recovered_u32 helper_call;
    recovered_u32 positive_fallback;
    recovered_u32 fifo_address;
    recovered_u32 command_29;
    recovered_u32 command_30;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8cb00_response_state_bridge_result;

recovered_startup_mode4_arm_8cb00_response_state_bridge_result
recovered_startup_mode4_arm_8cb00_response_state_bridge(
    recovered_u32 first_fifo_response, recovered_u32 second_fifo_response,
    recovered_u32 current_record_8, recovered_u32 current_record_10,
    recovered_u32 timing_5770f0, recovered_u32 helper_result)
{
    recovered_startup_mode4_arm_8cb00_response_state_bridge_result result;
    recovered_float_bits helper;

    result.first_fifo_response = first_fifo_response;
    result.second_fifo_response = second_fifo_response;
    result.current_record_8 = current_record_8;
    result.current_record_10 = current_record_10;
    result.state_51c940 = first_fifo_response;
    result.state_51c948 = 0x42200000U;
    result.state_51c950 = first_fifo_response - current_record_8;
    result.state_51c954 = second_fifo_response + current_record_10;
    result.timing_5770f0 = timing_5770f0;
    result.adjusted_timing = timing_5770f0 - 3U;
    result.helper_result = helper_result;
    helper.bits = helper_result;
    result.selected_float = helper.value <= 0.0F ? helper_result : 0x41f00000U;
    result.timing_zero_path = timing_5770f0 == 0U ? 1U : 0U;
    result.command_29_packet[0] = 29U;
    result.command_29_packet[1] = (first_fifo_response + 0x3000U) & 0xffffU;
    result.command_29_packet[2] = 0x42200000U;
    result.command_30_packet[0] = 30U;
    result.command_30_packet[1] = result.command_29_packet[1];
    result.command_30_packet[2] = 0x42200000U;
    result.helper_input_x = 0x40U;
    result.helper_input_y = 0x42U;
    result.helper_call = 0x0006ece0U;
    result.positive_fallback = 0x41f00000U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command_29 = 29U;
    result.command_30 = 30U;
    result.continuation = 0x0008cc0cU;
    return result;
}
