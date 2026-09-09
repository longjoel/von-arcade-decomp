/* State-2 grid seed phase recovered from i960 0xe66b4-0xe6708. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 source_base;
    recovered_u32 source_stride;
    recovered_u32 source_count;
    recovered_u32 frame_record_stride;
    recovered_u32 frame_word40_offset;
    recovered_u32 frame_word44_offset;
    recovered_u32 initial_word40;
    recovered_u32 initial_word44;
    int32_t source_sum;
    int32_t normalized_sum;
    recovered_u32 next_target;
} recovered_status_state2_grid_seed_result_e66b4;

recovered_status_state2_grid_seed_result_e66b4
recovered_status_state2_grid_seed_e66b4(int32_t source_sum)
{
    recovered_status_state2_grid_seed_result_e66b4 result;

    result.source_base = 0x01d000a4U;
    result.source_stride = 16U;
    result.source_count = 10U;
    result.frame_record_stride = 12U;
    result.frame_word40_offset = 0x40U;
    result.frame_word44_offset = 0x44U;
    result.initial_word40 = 0xffffffffU;
    result.initial_word44 = 0;
    result.source_sum = source_sum;
    result.normalized_sum = source_sum > 0 ? source_sum : 1;
    result.next_target = 0x000e6708U;
    return result;
}
