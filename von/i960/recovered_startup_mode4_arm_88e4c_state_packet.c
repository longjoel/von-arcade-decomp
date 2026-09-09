/* Selector-0 state packet suffix recovered from i960 0x88e4c-0x88e9c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 computed_word;
    recovered_u32 state_51c948;
    recovered_u32 computed_g7;
    recovered_u32 fifo_response;
    recovered_u32 record_30;
    recovered_u32 state_51c94c;
    recovered_u32 state_51c944;
    recovered_u32 packet_10[3];
    recovered_u32 fifo_address;
    recovered_u32 branch_target;
    recovered_u32 packet_command;
} recovered_startup_mode4_arm_88e4c_state_packet_result;

recovered_startup_mode4_arm_88e4c_state_packet_result
recovered_startup_mode4_arm_88e4c_state_packet(
    recovered_u32 computed_word, recovered_u32 state_51c948,
    recovered_u32 computed_g7, recovered_u32 fifo_response,
    recovered_u32 record_30)
{
    recovered_startup_mode4_arm_88e4c_state_packet_result result;

    result.computed_word = computed_word;
    result.state_51c948 = state_51c948;
    result.computed_g7 = computed_g7;
    result.fifo_response = fifo_response;
    result.record_30 = record_30;
    result.state_51c94c = computed_g7;
    result.state_51c944 = fifo_response;
    result.packet_10[0] = 10U;
    result.packet_10[1] = state_51c948;
    result.packet_10[2] = computed_word;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.branch_target = record_30 == 0U ? 0x00089ad8U : 0x00089ac8U;
    result.packet_command = 10U;
    return result;
}
