/* Selector-4 floating/state tail recovered from i960 0x899d8-0x89ac4. */
#include "recovered_common.h"

typedef union {
    recovered_u32 bits;
    float value;
} recovered_float_bits;

typedef struct {
    recovered_u32 helper_result;
    recovered_u32 record_0c;
    recovered_u32 prior_51c940;
    recovered_u32 state_51c948;
    recovered_u32 second_fifo_response;
    recovered_u32 record_30;
    recovered_u32 selected_float;
    recovered_u32 computed_command_word;
    recovered_u32 packet_10[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 state_51c94c;
    recovered_u32 state_51c9b4;
    recovered_u32 helper_call;
    recovered_u32 fifo_address;
    recovered_u32 command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_899d8_float_tail_result;

static recovered_u32 recovered_float_subtract(recovered_u32 left,
                                               recovered_u32 right)
{
    recovered_float_bits lhs;
    recovered_float_bits rhs;
    recovered_float_bits result;

    lhs.bits = left;
    rhs.bits = right;
    result.value = lhs.value - rhs.value;
    return result.bits;
}

recovered_startup_mode4_arm_899d8_float_tail_result
recovered_startup_mode4_arm_899d8_float_tail(
    recovered_u32 helper_result, recovered_u32 record_0c,
    recovered_u32 prior_51c940, recovered_u32 state_51c948, recovered_u32 second_fifo_response,
    recovered_u32 record_30, recovered_u32 g14_fallback)
{
    recovered_startup_mode4_arm_899d8_float_tail_result result;
    recovered_float_bits helper;

    helper.bits = helper_result;
    result.helper_result = helper_result;
    result.record_0c = record_0c;
    result.prior_51c940 = prior_51c940;
    result.state_51c948 = state_51c948;
    result.second_fifo_response = second_fifo_response;
    result.record_30 = record_30;
    result.selected_float = helper.value <= 0.0F ? helper_result : 0x41f00000U;
    result.computed_command_word = recovered_float_subtract(
        result.selected_float, record_0c);
    result.packet_10[0] = 10U;
    result.packet_10[1] = state_51c948;
    result.packet_10[2] = result.computed_command_word;
    result.state_51c940 = prior_51c940;
    result.state_51c944 = second_fifo_response;
    result.state_51c94c = result.selected_float;
    result.state_51c9b4 = record_30 == 0U ? 1U : g14_fallback;
    result.helper_call = 0x0006ece0U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command = 10U;
    result.continuation = record_30 == 0U ? 0x00089ac8U : 0x00089ad8U;
    return result;
}
