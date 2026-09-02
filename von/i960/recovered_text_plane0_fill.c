/* Address/value plan for the explicit-position fill helper at 0x1df70. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_text_plane0_fill_cell {
    u32 destination_byte_address;
    u32 value;
};

u32 recovered_text_plane0_fill_cell_plan(u32 column, u32 row,
                                         u32 width, u32 height,
                                         u32 y, u32 x, u32 fill_value,
                                         struct recovered_text_plane0_fill_cell *plan)
{
    if (y >= height || x >= width)
        return 0U;
    plan->destination_byte_address = 0x01000000U
        + ((((row + y) << 6) + column + x) << 1);
    plan->value = fill_value;
    return 1U;
}
