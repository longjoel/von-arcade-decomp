/* State-2 grid matching pass recovered from i960 0xe6708-0xe67f4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 source_base;
    recovered_u32 source_stride;
    recovered_u32 row_count;
    recovered_u32 column_count;
    recovered_u32 frame_record_stride;
    recovered_u32 frame_word40_offset;
    recovered_u32 frame_word44_offset;
    recovered_u32 frame_word48_offset;
    recovered_u32 percentage_scale;
    recovered_u32 next_row_target;
    recovered_u32 after_rows_target;
    int32_t source_value;
    int32_t normalized_sum;
    int32_t percentage;
} recovered_status_state2_grid_match_result_e6708;

recovered_status_state2_grid_match_result_e6708
recovered_status_state2_grid_match_e6708(int32_t source_value,
                                         int32_t normalized_sum)
{
    recovered_status_state2_grid_match_result_e6708 result;

    result.source_base = 0x01d000a4U;
    result.source_stride = 16U;
    result.row_count = 8U;
    result.column_count = 8U;
    result.frame_record_stride = 12U;
    result.frame_word40_offset = 0x40U;
    result.frame_word44_offset = 0x44U;
    result.frame_word48_offset = 0x48U;
    result.percentage_scale = 100U;
    result.next_row_target = 0x000e6714U;
    result.after_rows_target = 0x000e67f4U;
    result.source_value = source_value;
    result.normalized_sum = normalized_sum;
    result.percentage = normalized_sum != 0 ?
        (source_value * 100) / normalized_sum : 0;
    return result;
}
