/* Status string/glyph selector recovered from i960 0x23560-0x23610. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_string_glyph_plan {
    u32 saved_origin_column_address;
    u32 saved_origin_row_address;
    u32 restored_origin_column_address;
    u32 restored_origin_row_address;
    u32 glyph_helper;
    u32 attributes;
    u32 has_lowercase_suffix;
    u32 selected_index;
    u32 selected_character;
    u32 font_mode;
};

void recovered_status_string_glyph_plan(
    const uint8_t *text, struct recovered_status_string_glyph_plan *plan)
{
    const uint8_t *cursor = text;
    u32 has_lowercase = 0U;

    plan->saved_origin_column_address = 0x00504d40U;
    plan->saved_origin_row_address = 0x00504d44U;
    plan->restored_origin_column_address = 0x00504d40U;
    plan->restored_origin_row_address = 0x00504d44U;
    plan->glyph_helper = 0x0001d310U;
    plan->attributes = 0x4000U;

    if (*cursor != 0U) {
        ++cursor;
        while (*cursor != 0U) {
            if (*cursor >= (uint8_t)'a' && *cursor <= (uint8_t)'z')
                has_lowercase = 1U;
            ++cursor;
        }
    }

    plan->has_lowercase_suffix = has_lowercase;
    plan->selected_index = has_lowercase ? 0U : 1U;
    plan->selected_character = text[plan->selected_index];
    plan->font_mode = has_lowercase ? 0U : 1U;
}
