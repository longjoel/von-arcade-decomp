/* Pure selector plan for the alternate status glyph sink at 0x1d570. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_glyph_source_kind {
    RECOVERED_STATUS_GLYPH_DESCRIPTOR = 0,
    RECOVERED_STATUS_GLYPH_SPECIAL = 1,
};

struct recovered_status_glyph_plan {
    u32 glyph_index;
    u32 source_kind;
    u32 source;
    u32 descriptor;
    u32 rows;
    u32 adjustment;
};

void recovered_text_status_glyph_plan(u32 character,
                                      u32 *descriptor_adjustment,
                                      struct recovered_status_glyph_plan *plan)
{
    u32 index = (character & 0x7fU) - 0x20U;

    if (index > 95U)
        index = 0U;

    plan->glyph_index = index;
    plan->source_kind = (index == 41U || index == 42U)
        ? RECOVERED_STATUS_GLYPH_SPECIAL
        : RECOVERED_STATUS_GLYPH_DESCRIPTOR;
    plan->source = index == 41U ? 0x02fd7c90U
        : index == 42U ? 0x02fd7c98U : 0U;
    plan->descriptor = index * 8U + 0x02ea14d0U;
    plan->rows = 2U;
    plan->adjustment = descriptor_adjustment ? *descriptor_adjustment : 0U;
}
