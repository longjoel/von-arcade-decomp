/* Recovered tile-block writer at i960 0x0001de80. */

#include <stdint.h>

/*
 * The ROM loads the current text column/row from 0x504ce0/0x504ce4 and writes
 * a width-by-height rectangle into the 0x01004000 tile plane. Each source
 * halfword is stored with bit 15 forced, and each destination row has a
 * 64-tile stride.
 */
void recovered_text_write_tile_block(uint16_t *destination,
                                    const uint16_t *source,
                                    uint32_t column,
                                    uint32_t row,
                                    uint32_t width,
                                    uint32_t height)
{
    uint32_t y;
    uint32_t x;

    for (y = 0U; y < height; ++y) {
        for (x = 0U; x < width; ++x)
            destination[((row + y) << 6) + column + x] = (uint16_t)(source[y * width + x] | 0x8000U);
    }
}
