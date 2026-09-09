/* Gate-1 packet/state tail recovered from i960 0x8ce14-0x8d090. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 command_31_word[6];
    recovered_u32 command_29_word[2];
    recovered_u32 command_30_word[2];
    recovered_u32 command_10_word[4];
    recovered_u32 response_51c948;
    recovered_u32 response_51c958;
    recovered_u32 response_51c960;
    recovered_u32 response_51c940;
    recovered_u32 response_51c944;
    recovered_u32 response_51c94c;
    recovered_u32 response_51c95c;
    recovered_u32 record_30;
    recovered_u32 command_31_packet[7];
    recovered_u32 command_29_packet[3];
    recovered_u32 command_30_packet[3];
    recovered_u32 command_10_packet_0[3];
    recovered_u32 command_10_packet_1[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 state_51c948;
    recovered_u32 state_51c958;
    recovered_u32 state_51c960;
    recovered_u32 state_51c94c;
    recovered_u32 state_51c95c;
    recovered_u32 fifo_address;
    recovered_u32 command_31;
    recovered_u32 command_29;
    recovered_u32 command_30;
    recovered_u32 command_10;
    recovered_u32 record_zero_path;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8ce14_packet_state_tail_result;

recovered_startup_mode4_arm_8ce14_packet_state_tail_result
recovered_startup_mode4_arm_8ce14_packet_state_tail(
    const recovered_u32 command_31_word[6],
    const recovered_u32 command_29_word[2],
    const recovered_u32 command_30_word[2],
    const recovered_u32 command_10_word[4], recovered_u32 response_51c948,
    recovered_u32 response_51c958, recovered_u32 response_51c960,
    recovered_u32 response_51c940, recovered_u32 response_51c944,
    recovered_u32 response_51c94c, recovered_u32 response_51c95c,
    recovered_u32 record_30)
{
    recovered_startup_mode4_arm_8ce14_packet_state_tail_result result;

    for (recovered_u32 index = 0U; index < 6U; ++index)
        result.command_31_word[index] = command_31_word[index];
    for (recovered_u32 index = 0U; index < 2U; ++index) {
        result.command_29_word[index] = command_29_word[index];
        result.command_30_word[index] = command_30_word[index];
    }
    for (recovered_u32 index = 0U; index < 4U; ++index)
        result.command_10_word[index] = command_10_word[index];
    result.response_51c948 = response_51c948;
    result.response_51c958 = response_51c958;
    result.response_51c960 = response_51c960;
    result.response_51c940 = response_51c940;
    result.response_51c944 = response_51c944;
    result.response_51c94c = response_51c94c;
    result.response_51c95c = response_51c95c;
    result.record_30 = record_30;
    result.command_31_packet[0] = 31U;
    for (recovered_u32 index = 0U; index < 6U; ++index)
        result.command_31_packet[index + 1U] = command_31_word[index];
    result.command_29_packet[0] = 29U;
    result.command_29_packet[1] = command_29_word[0];
    result.command_29_packet[2] = command_29_word[1];
    result.command_30_packet[0] = 30U;
    result.command_30_packet[1] = command_30_word[0];
    result.command_30_packet[2] = command_30_word[1];
    result.command_10_packet_0[0] = 10U;
    result.command_10_packet_0[1] = command_10_word[0];
    result.command_10_packet_0[2] = command_10_word[1];
    result.command_10_packet_1[0] = 10U;
    result.command_10_packet_1[1] = command_10_word[2];
    result.command_10_packet_1[2] = command_10_word[3];
    result.state_51c940 = response_51c940;
    result.state_51c944 = response_51c944;
    result.state_51c948 = response_51c948;
    result.state_51c958 = response_51c958;
    result.state_51c960 = response_51c960;
    result.state_51c94c = response_51c94c;
    result.state_51c95c = response_51c95c;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command_31 = 31U;
    result.command_29 = 29U;
    result.command_30 = 30U;
    result.command_10 = 10U;
    result.record_zero_path = record_30 == 0U ? 1U : 0U;
    result.continuation = record_30 == 0U ? 0x0008d094U : 0x0008d0a4U;
    return result;
}
