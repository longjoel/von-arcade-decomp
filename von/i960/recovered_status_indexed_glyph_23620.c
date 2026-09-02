/* Indexed status glyph wrapper recovered from i960 0x23620-0x23668. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_indexed_glyph_plan {
    u32 source;
    u32 source_index;
    u32 selected_character;
    u32 helper;
    u32 saved_origin_column_address;
    u32 saved_origin_row_address;
    u32 restored_origin_column_address;
    u32 restored_origin_row_address;
};

void recovered_status_indexed_glyph_plan(
    const uint8_t *text, u32 index,
    struct recovered_status_indexed_glyph_plan *plan)
{
    plan->source = 0U; /* caller supplies the string pointer in g0 */
    plan->source_index = index;
    plan->selected_character = text[index];
    plan->helper = 0x0001cd18U;
    plan->saved_origin_column_address = 0x00504d44U;
    plan->saved_origin_row_address = 0x00504d40U;
    plan->restored_origin_column_address = 0x00504d44U;
    plan->restored_origin_row_address = 0x00504d40U;
}
