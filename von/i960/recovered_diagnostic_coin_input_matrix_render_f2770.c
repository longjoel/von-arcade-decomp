/* Coin/input matrix renderer contract recovered from i960 0xf2770-f2930. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 title_x, title_y, title_string, title_renderer;
    recovered_u32 matrix_builder, first_x, first_y_address, first_y_value;
    recovered_u32 second_x, second_y_address, second_y_value;
    recovered_u32 first_mode_address, first_mode_value, first_string;
    recovered_u32 second_mode_address, second_mode_value, second_string;
    recovered_u32 first_zero_string, first_value_string, second_zero_string, second_value_string;
    recovered_u32 return_target;
} recovered_diagnostic_coin_input_matrix_render_result_f2770;

int
recovered_diagnostic_coin_input_matrix_render_f2770(
    recovered_u32 first_mode, recovered_u32 second_mode,
    recovered_u32 first_value, recovered_u32 second_value,
    recovered_diagnostic_coin_input_matrix_render_result_f2770 *result)
{
    recovered_diagnostic_coin_input_matrix_render_result_f2770 local = {0};
    local.title_x=18U; local.title_y=6U; local.title_string=0x000eafd0U;
    local.title_renderer=0x000eaf20U; local.matrix_builder=0x000f23e0U;
    local.first_x=17U; local.first_y_address=0x01d00030U; local.first_y_value=first_value;
    local.second_x=27U; local.second_y_address=0x01d00032U; local.second_y_value=second_value;
    local.first_mode_address=0x01d00035U; local.first_mode_value=first_mode;
    local.second_mode_address=0x01d00036U; local.second_mode_value=second_mode;
    local.first_zero_string=0x000f2670U; local.first_value_string=0x000f2690U;
    local.second_zero_string=0x000f26d0U; local.second_value_string=0x000f26f0U;
    local.first_string=(first_mode==1U) ? local.first_zero_string : local.first_value_string;
    local.second_string=(second_mode==0U) ? local.second_zero_string : local.second_value_string;
    local.return_target=0x000f2930U;
    if (result != (void *)0) *result=local;
    return 1;
}
