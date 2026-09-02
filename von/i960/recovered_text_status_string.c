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
