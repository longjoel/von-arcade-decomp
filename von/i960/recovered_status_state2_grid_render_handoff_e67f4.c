/* State-2 grid render handoff recovered from i960 0xe67f4-0xe6c50. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 frame_record_stride;
    recovered_u32 rendered_row_count;
    recovered_u32 first_text_column;
    recovered_u32 text_column_stride;
    recovered_u32 renderer_target;
    recovered_u32 renderer_call_count;
    recovered_u32 frame_selector_offsets[4];
    recovered_u32 renderer_arg0[4];
    recovered_u32 renderer_arg1[4];
    recovered_u32 loop_target;
    recovered_u32 profile_dispatch_target;
    recovered_u32 next_target;
} recovered_status_state2_grid_render_handoff_result_e67f4;

recovered_status_state2_grid_render_handoff_result_e67f4
recovered_status_state2_grid_render_handoff_e67f4(void)
{
    recovered_status_state2_grid_render_handoff_result_e67f4 result = {
        12U, 4U, 19U, 3U, 0x0001d880U, 4U,
        {0x40U, 0x4cU, 0x58U, 0x64U},
        {2U, 31U, 2U, 31U},
        {13U, 16U, 25U, 28U},
        0x000e6818U, 0x000e6500U, 0x000e6c50U
    };
    return result;
}
