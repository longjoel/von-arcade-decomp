/* Selector-3 scale/state and response tail recovered from i960 0x8c840-0x8c96c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 selected_float;
    recovered_u32 record_0c;
    recovered_u32 response_51c948;
    recovered_u32 computed_state_51c94c;
    recovered_u32 command_10_word;
    recovered_u32 response_word;
    recovered_u32 record_30;
    recovered_u32 command_10_packet[3];
    recovered_u32 state_51c94c;
    recovered_u32 state_51c944;
    recovered_u32 backup_51c964;
    recovered_u32 backup_51c968;
    recovered_u32 backup_51c96c;
    recovered_u32 backup_51c970;
    recovered_u32 backup_51c974;
    recovered_u32 backup_51c978;
    recovered_u32 command_10;
    recovered_u32 fifo_address;
    recovered_u32 record_zero_path;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8c840_scale_packet_tail_result;

recovered_startup_mode4_arm_8c840_scale_packet_tail_result
recovered_startup_mode4_arm_8c840_scale_packet_tail(
    recovered_u32 selected_float, recovered_u32 record_0c,
    recovered_u32 response_51c948, recovered_u32 computed_state_51c94c,
    recovered_u32 command_10_word, recovered_u32 response_word,
    recovered_u32 record_30, recovered_u32 state_51c950,
    recovered_u32 rolling_51c958, recovered_u32 state_51c954,
    recovered_u32 rolling_51c95c, recovered_u32 rolling_51c960)
{
    recovered_startup_mode4_arm_8c840_scale_packet_tail_result result;

    result.selected_float = selected_float;
    result.record_0c = record_0c;
    result.response_51c948 = response_51c948;
    result.computed_state_51c94c = computed_state_51c94c;
    result.command_10_word = command_10_word;
    result.response_word = response_word;
    result.record_30 = record_30;
    result.command_10_packet[0] = 10U;
    result.command_10_packet[1] = response_51c948;
    result.command_10_packet[2] = command_10_word;
    result.state_51c94c = computed_state_51c94c;
    result.state_51c944 = response_word;
    result.backup_51c964 = state_51c950;
    result.backup_51c968 = computed_state_51c94c;
    result.backup_51c96c = state_51c954;
    result.backup_51c970 = rolling_51c958;
    result.backup_51c974 = rolling_51c95c;
    result.backup_51c978 = rolling_51c960;
    result.command_10 = 10U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.record_zero_path = record_30 == 0U ? 1U : 0U;
    result.continuation = record_30 == 0U ? 0x0008c8f4U : 0x0008c904U;
    return result;
}
