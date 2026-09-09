/* Shared state/packet bridge recovered from i960 0x8b678-0x8b740. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 flag_51d5e0;
    recovered_u32 candidate_51d5e4;
    recovered_u32 state_51c9b8;
    recovered_u32 retry_51c9bc;
    recovered_u32 retry_limit;
    recovered_u32 retry_active;
    recovered_u32 published_word_51c988;
    recovered_u32 delta_10;
    recovered_u32 delta_8;
    recovered_u32 packet_command;
    recovered_u32 packet_selector;
    recovered_u32 fifo_response;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8b678_state_packet_bridge_result;

recovered_startup_mode4_arm_8b678_state_packet_bridge_result
recovered_startup_mode4_arm_8b678_state_packet_bridge(
    recovered_u32 flag_51d5e0, recovered_u32 candidate_51d5e4,
    recovered_u32 state_51c9b8, recovered_u32 retry_51c9bc,
    recovered_u32 retry_word, recovered_u32 g30_value,
    recovered_u32 current_10, recovered_u32 linked_10,
    recovered_u32 current_8, recovered_u32 linked_8,
    recovered_u32 selector_51c99c, recovered_u32 fifo_response)
{
    recovered_startup_mode4_arm_8b678_state_packet_bridge_result result;

    result.flag_51d5e0 = flag_51d5e0;
    result.candidate_51d5e4 = candidate_51d5e4;
    result.state_51c9b8 = state_51c9b8;
    result.retry_51c9bc = retry_51c9bc;
    result.retry_limit = 26U;
    result.retry_active = 0U;
    result.published_word_51c988 = 0U;
    if (flag_51d5e0 == 0U) {
        if (candidate_51d5e4 == state_51c9b8)
            result.flag_51d5e0 = 1U;
    } else if (flag_51d5e0 == 1U) {
        result.retry_51c9bc = retry_51c9bc + 1U;
        if (result.retry_51c9bc < 26U) {
            result.published_word_51c988 = 31U + g30_value;
            result.flag_51d5e0 = retry_word;
            result.retry_active = 1U;
        }
    }
    result.delta_10 = current_10 - linked_10;
    result.delta_8 = current_8 - linked_8;
    result.packet_command = 10U;
    result.packet_selector = selector_51c99c;
    result.fifo_response = fifo_response;
    result.continuation = 0x0008b740U;
    return result;
}
