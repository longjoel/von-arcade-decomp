/* State-2 per-row status rendering plan recovered from i960 0xe6818-0xe6930. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 row_count;
    recovered_u32 frame_record_stride;
    recovered_u32 frame_word40_offset;
    recovered_u32 frame_word48_offset;
    recovered_u32 first_text_column;
    recovered_u32 text_column_stride;
    recovered_u32 even_formatter;
    recovered_u32 odd_formatter;
    recovered_u32 even_helper_argument;
    recovered_u32 odd_helper_argument;
    recovered_u32 formatter_target;
    recovered_u32 lookup_target;
    recovered_u32 numeric_target;
    recovered_u32 suffix_target;
    recovered_u32 suffix_formatter_target;
    recovered_u32 row_formatter[4];
    recovered_u32 row_helper_argument[4];
    recovered_u32 row_frame_offset[4];
    recovered_u32 row_text_column[4];
    recovered_u32 next_target;
} recovered_status_state2_grid_row_render_result_e6818;

recovered_status_state2_grid_row_render_result_e6818
recovered_status_state2_grid_row_render_e6818(void)
{
    recovered_status_state2_grid_row_render_result_e6818 result = {
        4U, 12U, 0x40U, 0x48U, 19U, 3U,
        8U, 16U, 13U, 21U,
        0x0001cac8U, 0x000e3a00U, 0x000e3a60U, 0x000e665cU,
        0x0001d9e0U,
        {8U, 16U, 8U, 16U},
        {13U, 21U, 13U, 21U},
        {0U, 12U, 24U, 36U},
        {19U, 22U, 25U, 28U},
        0x000e6930U
    };
    return result;
}
