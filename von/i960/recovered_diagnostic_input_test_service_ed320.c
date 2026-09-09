/* Diagnostic input-test state machine recovered from i960 0xed320-ed438. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_before, state_after, result_state_initialized;
    recovered_u32 initial_format_call, initial_format_x, initial_format_y;
    recovered_u32 hardware_word_a, hardware_word_b, combined_status;
    recovered_u32 external_service_call, input_format_call, input_format_x, input_format_y;
    recovered_u32 input_format_string, fallback_call, fallback_status_value;
    recovered_u32 final_wrapper_call, final_wrapper_x, final_wrapper_y, final_wrapper_string;
    recovered_u32 fallback_save_address, return_target;
} recovered_diagnostic_input_test_service_result_ed320;

recovered_diagnostic_input_test_service_result_ed320
recovered_diagnostic_input_test_service_ed320(
    recovered_u32 state, recovered_u32 hardware_word_a,
    recovered_u32 hardware_word_b, recovered_u32 external_result)
{
    recovered_diagnostic_input_test_service_result_ed320 result;
    result.state_before=state; result.state_after=state;
    result.result_state_initialized=1U; result.initial_format_call=0xeaf20U;
    result.initial_format_x=23U; result.initial_format_y=6U;
    result.hardware_word_a=hardware_word_a; result.hardware_word_b=hardware_word_b;
    result.combined_status=(hardware_word_a >> 1U) | hardware_word_b;
    result.external_service_call=0U; result.input_format_call=0U;
    result.input_format_x=0U; result.input_format_y=0U;
    result.input_format_string=0U; result.fallback_call=0U;
    result.fallback_status_value=0U; result.fallback_save_address=0x578500U;
    result.final_wrapper_call=0U; result.final_wrapper_x=0U; result.final_wrapper_y=0U;
    result.final_wrapper_string=0U;
    if (state == 1U) {
        result.state_after=2U; result.return_target=0xed438U;
        return result;
    }
    if (state > 2U) {
        result.state_after=state+1U; result.external_service_call=0x29330U;
        result.return_target=0xed438U; return result;
    }
    if (state == 2U) {
        result.state_after=3U; result.input_format_call=0x1cac8U;
        result.input_format_x=24U; result.input_format_y=17U;
        result.input_format_string=(result.combined_status & 2U) != 0U ? 0xed308U : 0xed304U;
    }
    result.final_wrapper_call=0xeaeb0U; result.final_wrapper_x=20U;
    result.final_wrapper_y=39U; result.final_wrapper_string=0xed1e0U;
    result.fallback_call=0xeade8U;
    result.fallback_status_value=external_result != 0U ? 2U : 0U;
    result.return_target=0xed438U;
    return result;
}
