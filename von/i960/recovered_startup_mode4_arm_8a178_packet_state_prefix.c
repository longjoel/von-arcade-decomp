/* Selector-2 downstream packet/state prefix recovered from i960 0x8a178-0x8a1c0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 timing_5770f0;
    recovered_u32 counter_51c984;
    recovered_u32 prior_fifo_response;
    recovered_u32 timing_minus_3;
    recovered_u32 timing_delta;
    recovered_u32 transformed_base;
    recovered_u32 state_51c940;
    recovered_u32 state_51c942;
    recovered_u32 fifo_address;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8a178_packet_state_prefix_result;

recovered_startup_mode4_arm_8a178_packet_state_prefix_result
recovered_startup_mode4_arm_8a178_packet_state_prefix(
    recovered_u32 timing_5770f0, recovered_u32 counter_51c984,
    recovered_u32 prior_fifo_response)
{
    recovered_startup_mode4_arm_8a178_packet_state_prefix_result result;

    result.timing_5770f0 = timing_5770f0;
    result.counter_51c984 = counter_51c984;
    result.prior_fifo_response = prior_fifo_response;
    result.timing_minus_3 = timing_5770f0 - 3U;
    result.timing_delta = 0xb4U - counter_51c984;
    result.transformed_base = prior_fifo_response + 0x1000U -
        (result.timing_delta << 8U);
    result.state_51c940 = result.transformed_base;
    result.state_51c942 = result.timing_delta;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.continuation = 0x0008a1c0U;
    return result;
}
