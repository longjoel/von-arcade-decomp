/* Runtime formatting wrappers recovered from i960 0xeaeb0-eaf30. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 variant;
    recovered_u32 input_value_g2;
    recovered_u32 helper_input_r4;
    recovered_u32 helper_output_r4;
    recovered_u32 pre_adjusted_g0;
    recovered_u32 board_byte;
    recovered_u32 selected_board_argument;
    recovered_u32 board_helper_address;
    recovered_u32 final_argument_g0;
    recovered_u32 numeric_helper_address;
    recovered_u32 final_helper_address;
    recovered_u32 return_address;
} recovered_runtime_format_wrappers_result_eaeb0;

recovered_runtime_format_wrappers_result_eaeb0
recovered_runtime_format_wrappers_eaeb0(
    recovered_u32 variant, recovered_u32 input_value_g2,
    recovered_u32 helper_output_r4, recovered_u32 initial_g0,
    recovered_u32 board_byte)
{
    recovered_runtime_format_wrappers_result_eaeb0 result;

    result.variant = variant;
    result.input_value_g2 = input_value_g2;
    result.helper_input_r4 = input_value_g2;
    result.helper_output_r4 = helper_output_r4;
    result.pre_adjusted_g0 = initial_g0 - 1U;
    result.board_byte = board_byte & 0xffU;
    result.selected_board_argument = 0U;
    result.board_helper_address = 0U;
    result.final_argument_g0 = helper_output_r4;
    result.numeric_helper_address = 0x0001cac8U;
    result.final_helper_address = 0x000f5100U;
    result.return_address = 0U;
    switch (variant) {
    case 0U:
        result.return_address = 0x000eaec0U;
        break;
    case 1U:
        result.selected_board_argument =
            result.board_byte == 1U || result.board_byte == 2U ? 32U : 42U;
        result.board_helper_address = 0x0001cc40U;
        result.final_argument_g0 = helper_output_r4;
        result.return_address = 0x000eaf1cU;
        break;
    case 2U:
        result.final_helper_address = 0x0001da90U;
        result.return_address = 0x000eaf30U;
        break;
    default:
        break;
    }
    return result;
}
