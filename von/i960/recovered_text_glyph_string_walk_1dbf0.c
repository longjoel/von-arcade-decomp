/* Pure route and walk contract for i960 0x1dbf0. */

#include <stdint.h>

typedef uint32_t u32;
typedef uint8_t u8;

u32 recovered_text_glyph_string_walk_1dbf0(const u8 *text,
                                           u32 *byte_count,
                                           u32 *callee)
{
    u32 count = 0U;

    while (text[count] != 0U)
        ++count;
    *byte_count = count;
    *callee = 0x0001d6a0U;
    return 1U;
}
