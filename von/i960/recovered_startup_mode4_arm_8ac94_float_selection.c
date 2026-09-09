/* Selector-1 helper-result selection recovered from i960 0x8ac94-0x8ad00. */
#include "recovered_common.h"

typedef union {
    recovered_u32 bits;
    float value;
} recovered_float_bits;

typedef struct {
    recovered_u32 helper_input_x;
    recovered_u32 helper_input_y;
    recovered_u32 helper_result;
    recovered_u32 selected_float;
    recovered_u32 adjusted_float;
    recovered_u32 timing_5770f0;
    recovered_u32 timing_zero_path;
    recovered_u32 helper_call;
    recovered_u32 positive_fallback;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8ac94_float_selection_result;

recovered_startup_mode4_arm_8ac94_float_selection_result
recovered_startup_mode4_arm_8ac94_float_selection(
    recovered_u32 helper_input_x, recovered_u32 helper_input_y,
    recovered_u32 helper_result, recovered_u32 timing_5770f0)
{
    recovered_startup_mode4_arm_8ac94_float_selection_result result;
    recovered_float_bits helper;
    recovered_float_bits selected;

    helper.bits = helper_result;
    result.helper_input_x = helper_input_x;
    result.helper_input_y = helper_input_y;
    result.helper_result = helper_result;
    result.selected_float = helper.value <= 0.0F ? helper_result : 0x41f00000U;
    selected.bits = result.selected_float;
    result.adjusted_float = selected.bits;
    result.timing_5770f0 = timing_5770f0;
    result.timing_zero_path = timing_5770f0 == 0U ? 1U : 0U;
    if (timing_5770f0 == 0U) {
        selected.value += 2.5F;
        result.adjusted_float = selected.bits;
    }
    result.helper_call = 0x0006ece0U;
    result.positive_fallback = 0x41f00000U;
    result.continuation = 0x0008ad00U;
    return result;
}
