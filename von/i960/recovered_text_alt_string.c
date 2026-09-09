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

struct recovered_text_alt_glyph_string_plan {
    u32 font_mode;
    u32 attributes;
    u32 renderer_target;
    u32 emits_characters;
};

/* Connect the 0x1d7d0 classifier to its shared 0x1d310 call shape. */
void recovered_text_alt_glyph_string_plan(
    const u8 *text,
    struct recovered_text_alt_glyph_string_plan *plan)
{
    plan->font_mode = recovered_text_alt_string_font_mode(text);
    plan->attributes = 0x4000U;
    plan->renderer_target = 0x0001d310U;
    plan->emits_characters = *text != 0U;
}
