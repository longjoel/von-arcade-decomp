/* Versus City billboard test layout recovered from i960 0xeda30-edcf8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 header_x, header_y, header_string;
    recovered_u32 pattern_helper, pattern_count, pattern_value[6];
    recovered_u32 state_address, hardware_flag_address, modulo_address;
    recovered_u32 winner_x, winner_y, winner_p1_string, winner_p2_string;
    recovered_u32 seven_segment_x, seven_segment_y, seven_segment_p1_string;
    recovered_u32 start_lamp_x, start_lamp_y, start_lamp_string;
    recovered_u32 status_word_address, wrapper_address, fallback_call;
    recovered_u32 return_target;
} recovered_diagnostic_billboard_test_render_result_eda30;

recovered_diagnostic_billboard_test_render_result_eda30
recovered_diagnostic_billboard_test_render_eda30(void)
{
    recovered_diagnostic_billboard_test_render_result_eda30 result = {
        21U, 6U, 0x000eaf80U,
        0x000184e8U, 6U, {0x1fU,0x3fU,0x5fU,0x7fU,0x97U,0x9fU},
        0x005785c4U, 0x00503a08U, 0x005024e8U,
        16U, 18U, 0x000ed9b0U, 0x000ed9c0U,
        16U, 28U, 0x000ed9d0U,
        16U, 28U, 0x000ed9f0U,
        0x00502484U, 0x000eaeb0U, 0x000eade8U,
        0x000edcf8U
    };
    return result;
}
