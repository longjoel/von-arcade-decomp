/* Selector-0 setup/helper selection recovered from i960 0x8b7e0-0x8b85c. */
#include "recovered_common.h"

typedef union {
    recovered_u32 bits;
    float value;
} recovered_float_bits;

typedef struct {
    recovered_u32 masked_operand;
    recovered_u32 adjusted_operand;
    recovered_u32 low_operand_path;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
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
} recovered_startup_mode4_arm_8b7e0_float_selection_result;

recovered_startup_mode4_arm_8b7e0_float_selection_result
recovered_startup_mode4_arm_8b7e0_float_selection(
    recovered_u32 masked_operand, recovered_u32 state_51c950,
    recovered_u32 state_51c954, recovered_u32 helper_result,
    recovered_u32 timing_5770f0)
{
    recovered_startup_mode4_arm_8b7e0_float_selection_result result;
    recovered_float_bits helper;
    recovered_float_bits selected;

    result.masked_operand = masked_operand;
    result.adjusted_operand = masked_operand - 3U;
    result.low_operand_path = (int32_t)result.adjusted_operand < 1 ? 1U : 0U;
    result.state_51c950 = state_51c950;
    result.state_51c954 = state_51c954;
    result.helper_input_x = 0x40U;
    result.helper_input_y = 0x42U;
    result.helper_result = helper_result;
    helper.bits = helper_result;
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
    result.continuation = 0x0008b85cU;
    return result;
}
