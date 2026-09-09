/* Selector-3 floating prefix recovered from i960 0x8a4bc-0x8a584. */
#include "recovered_common.h"

typedef union {
    recovered_u32 bits;
    float value;
} recovered_float_bits;

typedef struct {
    recovered_u32 timing_5770f0;
    recovered_u32 counter_51c984;
    recovered_u32 prior_fifo_response;
    recovered_u32 timing_delta;
    recovered_u32 timing_float_bits;
    recovered_u32 transformed_base;
    recovered_u32 state_51c940;
    recovered_u32 state_51c942;
    recovered_u32 helper_result;
    recovered_u32 selected_float;
    recovered_u32 timing_zero_path;
    recovered_u32 helper_call;
    recovered_u32 positive_fallback;
    recovered_u32 fifo_address;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8a4bc_float_prefix_result;

recovered_startup_mode4_arm_8a4bc_float_prefix_result
recovered_startup_mode4_arm_8a4bc_float_prefix(
    recovered_u32 timing_5770f0, recovered_u32 counter_51c984,
    recovered_u32 prior_fifo_response, recovered_u32 helper_result)
{
    recovered_startup_mode4_arm_8a4bc_float_prefix_result result;
    recovered_float_bits helper;
    recovered_float_bits timing_float;

    helper.bits = helper_result;
    timing_float.value = 0.0F;
    result.timing_5770f0 = timing_5770f0;
    result.counter_51c984 = counter_51c984;
    result.prior_fifo_response = prior_fifo_response;
    result.timing_delta = 0xb4U - counter_51c984;
    result.timing_float_bits = timing_float.bits;
    result.transformed_base = prior_fifo_response + 0x1000U -
        (result.timing_delta << 8U);
    result.state_51c940 = result.transformed_base;
    result.state_51c942 = result.timing_delta;
    result.helper_result = helper_result;
    result.selected_float = helper.value <= 0.0F ? helper_result : 0x41f00000U;
    result.timing_zero_path = timing_5770f0 == 0U ? 1U : 0U;
    result.helper_call = 0x0006ece0U;
    result.positive_fallback = 0x41f00000U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.continuation = 0x0008a584U;
    return result;
}
