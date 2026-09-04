/* Wide tile-pattern writers recovered from i960 0x22970-0x22a40. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_status_wide_tile_pattern {
    u32 base;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
    u32 tile_count;
    u32 first_value;
    u32 attribute_mask;
};

void recovered_status_wide_tile_pattern_plan(
    u32 variant, u32 column, u32 row,
    struct recovered_status_wide_tile_pattern *plan)
{
    plan->base = variant == 0U ? 0x01000000U : 0x01000034U;
    plan->column = column;
    plan->row = row;
    plan->width = variant == 0U ? 23U : variant == 1U ? 29U : 19U;
    plan->height = 2U;
    plan->tile_count = plan->width * plan->height;
    plan->first_value = variant == 0U ? 0x0000ffb0U
        : variant == 1U ? 0x0000fd10U : 0x0000ff40U;
    plan->attribute_mask = 0xc000U;
}

u32 recovered_status_wide_tile_pattern_value(u32 variant, u32 index)
{
    return 0xc000U + (variant == 0U ? 0x3db0U
        : variant == 1U ? 0x3d10U : 0x3f40U) + index;
}

u32 recovered_status_wide_tile_pattern_destination(
    u32 variant, u32 column, u32 row, u32 index)
{
    u32 width = variant == 0U ? 23U : variant == 1U ? 29U : 19U;
    return recovered_pattern_tile_address(
        variant == 0U ? 0x01000000U : 0x01000034U,
        column, row, index, width, 0U);
}
