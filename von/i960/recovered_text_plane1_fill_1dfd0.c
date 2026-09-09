/* Address/value plan for the plane-1 fill helper at 0x1dfd0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_text_plane1_fill_cell {
    u32 destination_byte_address;
    u32 value;
};

u32 recovered_text_plane1_fill_cell_plan(u32 column, u32 row,
                                         u32 width, u32 height,
                                         u32 y, u32 x, u32 fill_value,
                                         struct recovered_text_plane1_fill_cell *plan)
{
    /* 0x1dfd0 uses signed loop bounds, then writes g14 unchanged. */
    if ((int32_t)width <= 0 || (int32_t)height <= 0
            || y >= height || x >= width)
        return 0U;
    plan->destination_byte_address = 0x01002000U
        + ((((row + y) << 6) + column + x) << 1);
    plan->value = fill_value;
    return 1U;
}
