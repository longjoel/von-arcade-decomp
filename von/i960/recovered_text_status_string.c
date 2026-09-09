/* Pure classifier for the status-string writer at i960 0x1d880. */

#include <stdint.h>

typedef uint32_t u32;
typedef uint8_t u8;

struct recovered_status_string_plan {
    u32 font_mode;
    u32 emits_characters;
};

void recovered_text_status_string_plan(const u8 *text,
                                        struct recovered_status_string_plan *plan)
{
    const u8 *cursor = text;
    u32 has_lowercase = 0U;

    plan->font_mode = 1U;
    plan->emits_characters = *cursor != 0U;
    if (*cursor == 0U)
        return;

    ++cursor;
    while (*cursor != 0U) {
        if (*cursor >= (u8)'a' && *cursor <= (u8)'z')
            has_lowercase = 1U;
        ++cursor;
    }
    if (has_lowercase)
        plan->font_mode = 0U;
}

struct recovered_text_status_attributed_plan {
    u32 font_mode;
    u32 attributes;
    u32 renderer_target;
    u32 emits_characters;
};

/* Connect the 0x1d930 sibling to the shared attributed glyph renderer. */
void recovered_text_status_attributed_plan(
    const u8 *text,
    struct recovered_text_status_attributed_plan *plan)
{
    struct recovered_status_string_plan classifier;

    recovered_text_status_string_plan(text, &classifier);
    plan->font_mode = classifier.font_mode;
    plan->attributes = 0x4000U;
    plan->renderer_target = 0x0001d310U;
    plan->emits_characters = classifier.emits_characters;
}
