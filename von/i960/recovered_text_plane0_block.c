/* Address plan for the plain tile-plane block writer at i960 0x1dc10. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_text_plane0_cell {
    u32 source_byte_offset;
    u32 destination_byte_address;
    u32 source_word_or_mask;
};

u32 recovered_text_plane0_cell_plan(u32 column, u32 row, u32 width, u32 height,
                                    u32 y, u32 x, u32 source_word,
                                    struct recovered_text_plane0_cell *plan)
{
    if (y >= height || x >= width)
        return 0U;
    plan->source_byte_offset = ((y * width) + x) << 1;
    plan->destination_byte_address = 0x01000000U
        + ((((row + y) << 6) + column + x) << 1);
    plan->source_word_or_mask = source_word | 0x8000U;
    return 1U;
}
