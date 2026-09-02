/* Tile pattern writer recovered from i960 0x228f0-0x22960. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_tile_pattern_plan {
    u32 plane;
    u32 column;
    u32 first_row;
    u32 width;
    u32 height;
    u32 tile_count;
    u32 first_value;
    u32 attribute_mask;
};

void recovered_status_tile_pattern_plan(u32 column, u32 row,
                                        struct recovered_status_tile_pattern_plan *plan)
{
    plan->plane = 0x01000000U;
    plan->column = column;
    plan->first_row = row & 0x3fU;
    plan->width = 16U;
    plan->height = 7U;
    plan->tile_count = 112U;
    plan->first_value = 0x0000d488U;
    plan->attribute_mask = 0xc000U;
}

u32 recovered_status_tile_pattern_value(u32 index)
{
    return 0xc000U | (0x1488U + index);
}

u32 recovered_status_tile_pattern_destination(u32 column, u32 row, u32 index)
{
    u32 row_offset = (index / 16U + row) & 0x3fU;
    u32 column_offset = column + (index % 16U);
    return 0x01000000U + ((row_offset << 6) + column_offset) * 2U;
}
