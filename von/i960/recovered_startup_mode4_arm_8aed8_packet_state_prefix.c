/* Selector-2 post-dispatch prefix recovered from i960 0x8aed8-0x8af20. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 timing_5770f0;
    recovered_u32 counter_51c984;
    recovered_u32 prior_response_base;
    recovered_u32 timing_delta;
    recovered_u32 transformed_base;
    recovered_u32 state_51c940;
    recovered_u32 state_51c942;
    recovered_u32 helper_input_x;
    recovered_u32 helper_input_y;
    recovered_u32 helper_call;
    recovered_u32 fifo_address;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8aed8_packet_state_prefix_result;

recovered_startup_mode4_arm_8aed8_packet_state_prefix_result
recovered_startup_mode4_arm_8aed8_packet_state_prefix(
    recovered_u32 timing_5770f0, recovered_u32 counter_51c984,
    recovered_u32 prior_response_base, recovered_u32 helper_input_x,
    recovered_u32 helper_input_y)
{
    recovered_startup_mode4_arm_8aed8_packet_state_prefix_result result;

    result.timing_5770f0 = timing_5770f0;
    result.counter_51c984 = counter_51c984;
    result.prior_response_base = prior_response_base;
    result.timing_delta = 0xb4U - counter_51c984;
    result.transformed_base = prior_response_base + 0x1000U -
        (result.timing_delta << 8U);
    result.state_51c940 = result.transformed_base;
    result.state_51c942 = result.timing_delta << 8U;
    result.helper_input_x = helper_input_x;
    result.helper_input_y = helper_input_y;
    result.helper_call = 0x0006ece0U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.continuation = 0x0008af20U;
    return result;
}
