/* Selector-2 response tail recovered from i960 0x8a43c-0x8a4bc. */
#include "recovered_common.h"

typedef union {
    recovered_u32 bits;
    float value;
} recovered_float_bits;

typedef struct {
    recovered_u32 command_31_response;
    recovered_u32 computed_base_float;
    recovered_u32 linked_record_0c;
    recovered_u32 prior_state_51c950;
    recovered_u32 prior_state_51c954;
    recovered_u32 first_command_10_response;
    recovered_u32 second_command_10_response;
    recovered_u32 record_30;
    recovered_u32 command_10_packet[3];
    recovered_u32 command_10_float_delta;
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 fifo_address;
    recovered_u32 command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8a43c_response_tail_result;

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

recovered_startup_mode4_arm_8a43c_response_tail_result
recovered_startup_mode4_arm_8a43c_response_tail(
    recovered_u32 command_31_response, recovered_u32 computed_base_float,
    recovered_u32 linked_record_0c, recovered_u32 prior_state_51c950,
    recovered_u32 prior_state_51c954, recovered_u32 first_command_10_response,
    recovered_u32 second_command_10_response, recovered_u32 record_30)
{
    recovered_startup_mode4_arm_8a43c_response_tail_result result;

    result.command_31_response = command_31_response;
    result.computed_base_float = computed_base_float;
    result.linked_record_0c = linked_record_0c;
    result.prior_state_51c950 = prior_state_51c950;
    result.prior_state_51c954 = prior_state_51c954;
    result.first_command_10_response = first_command_10_response;
    result.second_command_10_response = second_command_10_response;
    result.record_30 = record_30;
    result.command_10_float_delta = recovered_float_subtract(
        computed_base_float, linked_record_0c);
    result.command_10_packet[0] = 10U;
    result.command_10_packet[1] = command_31_response;
    result.command_10_packet[2] = result.command_10_float_delta;
    result.state_51c940 = first_command_10_response;
    result.state_51c944 = second_command_10_response;
    result.state_51c950 = prior_state_51c950;
    result.state_51c954 = prior_state_51c954;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command = 10U;
    result.continuation = record_30 == 0U ? 0x0008a16cU : 0x0008a880U;
    return result;
}
