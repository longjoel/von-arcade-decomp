/* Status-render row tail recovered from i960 0xe5ebc-0xe5f48. */
#include <stdint.h>

typedef uint32_t recovered_u32;

typedef struct {
    recovered_u32 current_row;
    recovered_u32 next_row;
    recovered_u32 continue_loop;
    recovered_u32 current_record_offset;
    recovered_u32 next_record_offset;
    recovered_u32 current_text_column;
    recovered_u32 next_text_column;
    recovered_u32 record_base;
    recovered_u32 record_stride;
    recovered_u32 text_column_increment;
    recovered_u32 loop_limit;
    recovered_u32 continuation;
} recovered_status_render_row_advance_result_e5ebc;

/*
 * The row epilogue adds 8 to r6, adds 1 to r4, adds 3 to r5, and uses the
 * literal-first cmpi r4,4 / ble loop condition.  The initial row is zero,
 * so rows 0 through 4 are visited before the shared continuation.
 */
recovered_status_render_row_advance_result_e5ebc
recovered_status_render_row_advance_e5ebc(
    recovered_u32 current_row, recovered_u32 current_record_offset,
    recovered_u32 current_text_column)
{
    recovered_status_render_row_advance_result_e5ebc result;

    result.current_row = current_row;
    result.next_row = current_row + 1U;
    result.continue_loop = result.next_row <= 4U ? 1U : 0U;
    result.current_record_offset = current_record_offset;
    result.next_record_offset = current_record_offset + 8U;
    result.current_text_column = current_text_column;
    result.next_text_column = current_text_column + 3U;
    result.record_base = 0x00578410U;
    result.record_stride = 8U;
    result.text_column_increment = 3U;
    result.loop_limit = 4U;
    result.continuation = result.continue_loop ? 0x000e5e20U : 0x000e60d0U;
    return result;
}
