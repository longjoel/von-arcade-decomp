/* Input-test renderer layout recovered from i960 0xed5c0-ed968. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 header_x, header_y, header_string;
    recovered_u32 base_row_count, base_row_x[12], base_row_y[12], base_row_string[12];
    recovered_u32 conditional_row_count, conditional_flag_bit[12];
    recovered_u32 conditional_row_x[12], conditional_row_y[12];
    recovered_u32 conditional_string, prompt_x, prompt_y, prompt_string;
    recovered_u32 input_wrapper, renderer, flag_address, return_target;
} recovered_diagnostic_input_test_render_result_ed5c0;

recovered_diagnostic_input_test_render_result_ed5c0
recovered_diagnostic_input_test_render_ed5c0(void)
{
    recovered_diagnostic_input_test_render_result_ed5c0 result = {
        21U, 6U, 0x000eaf70U, 12U,
        {19U,19U,19U,19U,19U,19U,19U,19U,19U,19U,19U,19U},
        {11U,13U,15U,17U,19U,21U,23U,27U,30U,32U,34U,36U},
        {0x000ed440U,0x000ed460U,0x000ed480U,0x000ed4a0U,
         0x000ed4c0U,0x000ed4e0U,0x000ed500U,0x000ed520U,
         0x000ed540U,0x000ed560U,0x000ed580U,0x000ed5a0U},
        12U,
        {13U,12U,14U,15U,8U,9U,21U,20U,22U,23U,16U,17U},
        {34U,34U,34U,34U,34U,34U,39U,39U,39U,39U,39U,39U},
        {13U,15U,17U,19U,21U,23U,13U,15U,17U,19U,21U,23U},
        0x000ed5b4U, 20U, 39U, 0x000ed1e0U,
        0x000eaeb0U, 0x000f5100U, 0x0050249cU, 0x000ed968U
    };
    return result;
}
