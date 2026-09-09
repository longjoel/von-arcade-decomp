/* Selector-1 helper selection recovered from i960 0x8c358-0x8c3d0. */
#include "recovered_common.h"

typedef union {
    recovered_u32 bits;
    float value;
} recovered_float_bits;

typedef struct {
    recovered_u32 timing_5770f0;
    recovered_u32 adjusted_timing;
    recovered_u32 low_timing_path;
    recovered_u32 helper_result;
    recovered_u32 selected_float;
    recovered_u32 adjusted_float;
    recovered_u32 timing_zero_path;
    recovered_u32 helper_input_x;
    recovered_u32 helper_input_y;
    recovered_u32 helper_call;
    recovered_u32 positive_fallback;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8c358_float_selection_result;

recovered_startup_mode4_arm_8c358_float_selection_result
recovered_startup_mode4_arm_8c358_float_selection(
    recovered_u32 timing_5770f0, recovered_u32 helper_result)
{
    recovered_startup_mode4_arm_8c358_float_selection_result result;
    recovered_float_bits helper;
    recovered_float_bits selected;

    result.timing_5770f0 = timing_5770f0;
    result.adjusted_timing = timing_5770f0 - 3U;
    result.low_timing_path = (int32_t)result.adjusted_timing < 1 ? 1U : 0U;
    result.helper_result = helper_result;
    helper.bits = helper_result;
    result.selected_float = helper.value <= 0.0F ? helper_result : 0x41f00000U;
    selected.bits = result.selected_float;
    result.adjusted_float = selected.bits;
    result.timing_zero_path = timing_5770f0 == 0U ? 1U : 0U;
    if (timing_5770f0 == 0U) {
        selected.value += 2.5F;
        result.adjusted_float = selected.bits;
    }
    result.helper_input_x = 0x40U;
    result.helper_input_y = 0x42U;
    result.helper_call = 0x0006ece0U;
    result.positive_fallback = 0x41f00000U;
    result.continuation = 0x0008c3d0U;
    return result;
}
