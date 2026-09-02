/* Recovered alternate glyph-string mode selector at i960 0x0001d9e0. */

typedef unsigned int u32;
typedef unsigned char u8;

/*
 * The ROM scans after the first byte.  A lowercase ASCII byte selects glyph
 * bank 2; strings with no lowercase bytes select glyph bank 3.  The caller
 * then emits every byte through the shared glyph sink with zero attributes.
 */
u32 recovered_text_alt_string_font_mode(const u8 *text)
{
    const u8 *cursor = text;
    u32 mode = 3U;

    if (*cursor == 0U)
        return mode;

    ++cursor;
    while (*cursor != 0U) {
        if (*cursor >= (u8)'a' && *cursor <= (u8)'z')
            mode = 2U;
        ++cursor;
    }
    return mode;
}
