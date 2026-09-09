/* Selector-0 floating/packet tail recovered from i960 0x89cf4-0x89e44. */
#include "recovered_common.h"

typedef union {
    recovered_u32 bits;
    float value;
} recovered_float_bits;

typedef struct {
    recovered_u32 helper_result;
    recovered_u32 record_0c;
    recovered_u32 record_8;
    recovered_u32 record_10;
    recovered_u32 state_51c948;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 record_30;
    recovered_u32 first_fifo_response;
    recovered_u32 second_fifo_response;
    recovered_u32 selected_float;
    recovered_u32 derived_float_word;
    recovered_u32 packet_first_10[3];
    recovered_u32 packet_second_10[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 state_51c94c;
    recovered_u32 helper_call;
    recovered_u32 fifo_address;
    recovered_u32 first_command;
    recovered_u32 second_command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_89cf4_float_packet_tail_result;

static recovered_u32 recovered_float_add(recovered_u32 left, recovered_u32 right)
{
    recovered_float_bits lhs;
    recovered_float_bits rhs;
    recovered_float_bits result;

    lhs.bits = left;
    rhs.bits = right;
    result.value = lhs.value + rhs.value;
    return result.bits;
}

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

recovered_startup_mode4_arm_89cf4_float_packet_tail_result
recovered_startup_mode4_arm_89cf4_float_packet_tail(
    recovered_u32 helper_result, recovered_u32 record_0c,
    recovered_u32 record_8, recovered_u32 record_10,
    recovered_u32 state_51c948, recovered_u32 state_51c950,
    recovered_u32 state_51c954, recovered_u32 record_30,
    recovered_u32 first_fifo_response, recovered_u32 second_fifo_response)
{
    recovered_startup_mode4_arm_89cf4_float_packet_tail_result result;
    recovered_float_bits helper;

    helper.bits = helper_result;
    result.helper_result = helper_result;
    result.record_0c = record_0c;
    result.record_8 = record_8;
    result.record_10 = record_10;
    result.state_51c948 = state_51c948;
    result.state_51c950 = state_51c950;
    result.state_51c954 = state_51c954;
    result.record_30 = record_30;
    result.first_fifo_response = first_fifo_response;
    result.second_fifo_response = second_fifo_response;
    result.selected_float = helper.value <= 0.0F ? helper_result : 0x41f00000U;
    result.derived_float_word = recovered_float_subtract(
        recovered_float_add(result.selected_float, record_8), record_0c);
    result.packet_first_10[0] = 10U;
    result.packet_first_10[1] = record_10 - state_51c954;
    result.packet_first_10[2] = record_8 - state_51c950;
    result.packet_second_10[0] = 10U;
    result.packet_second_10[1] = state_51c948;
    result.packet_second_10[2] = result.derived_float_word;
    result.state_51c940 = first_fifo_response;
    result.state_51c944 = second_fifo_response;
    result.state_51c94c = recovered_float_add(result.selected_float, record_8);
    result.helper_call = 0x0006ece0U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.first_command = 10U;
    result.second_command = 10U;
    result.continuation = record_30 == 0U ? 0x0008a880U : 0x0008a16cU;
    return result;
}
