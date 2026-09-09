/* CRT pattern buffer fill recovered from i960 0xf08c0-f0938. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 destination_base;
    recovered_u32 plane_count, rows_per_plane, halfwords_per_row;
    recovered_u32 plane, row, halfword;
    recovered_u32 destination_address, pattern_value;
    recovered_u32 return_target;
} recovered_diagnostic_crt_pattern_buffer_fill_result_f08c0;

int
recovered_diagnostic_crt_pattern_buffer_fill_f08c0(
    recovered_u32 plane, recovered_u32 row, recovered_u32 halfword,
    recovered_diagnostic_crt_pattern_buffer_fill_result_f08c0 *result)
{
    recovered_diagnostic_crt_pattern_buffer_fill_result_f08c0 local;
    local.destination_base = 0x0100461eU;
    local.plane_count = 4U; local.rows_per_plane = 6U;
    local.halfwords_per_row = 32U;
    local.plane = plane; local.row = row; local.halfword = halfword;
    local.destination_address = 0U; local.pattern_value = 0U;
    local.return_target = 0x000f0938U;
    if (plane >= 4U || row >= 6U || halfword >= 32U) {
        if (result != (recovered_diagnostic_crt_pattern_buffer_fill_result_f08c0 *)0)
            *result = local;
        return 0;
    }
    local.destination_address = local.destination_base +
        ((row + plane * 6U) << 7U) + (halfword << 1U);
    local.pattern_value = 0x2000U +
        ((plane * 4U + (halfword >> 3U)) << 7U) + (halfword & 7U);
    if (result != (recovered_diagnostic_crt_pattern_buffer_fill_result_f08c0 *)0)
        *result = local;
    return 1;
}
