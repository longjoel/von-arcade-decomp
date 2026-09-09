/* Mode-9 response publication recovered from i960 0xdea6c-0xdea94. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 response_first;
    recovered_u32 response_second;
    recovered_u32 response_gate;
} recovered_startup_mode9_response_gate_input_dea6c;

typedef struct {
    recovered_u32 frame_pair[2];
    recovered_u32 gate_is_zero;
    recovered_u32 continuation;
    recovered_u32 frame_output_offset;
    recovered_u32 frame_aux_offset;
} recovered_startup_mode9_response_gate_result_dea6c;

/*
 * The first two FIFO reads are published at fp+0x40 and fp+0x44.  A third
 * read gates the floating reconstruction: zero returns at 0xdead0, while a
 * nonzero value enters the transform beginning at 0xdea94.
 */
void recovered_startup_mode9_response_gate_dea6c(
    const recovered_startup_mode9_response_gate_input_dea6c *input,
    recovered_startup_mode9_response_gate_result_dea6c *result)
{
    result->frame_pair[0] = input->response_first;
    result->frame_pair[1] = input->response_second;
    result->gate_is_zero = input->response_gate == 0U ? 1U : 0U;
    result->continuation = result->gate_is_zero ? 0x000dead0U : 0x000dea94U;
    result->frame_output_offset = 0x40U;
    result->frame_aux_offset = 0x44U;
}
