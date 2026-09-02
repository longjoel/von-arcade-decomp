/* Text-mode setup and helper dispatch recovered from i960 0x1f010. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_text_mode_helper {
    RECOVERED_TEXT_MODE_GLYPH_BLOCK = 0,
    RECOVERED_TEXT_MODE_GLYPH_DIRECT = 1,
};

struct recovered_text_mode_setup_plan {
    u32 timing_cdc;
    u32 timing_ce0;
    u32 timing_ce4;
    u32 helper;
    u32 source;
    u32 tile;
    u32 width;
};

void recovered_text_mode_setup_plan(u32 mode, u32 caller_g10, u32 caller_g13,
                                    struct recovered_text_mode_setup_plan *plan)
{
    plan->timing_cdc = caller_g10 + 31;
    plan->timing_ce0 = caller_g10 + 31;
    plan->timing_ce4 = caller_g13 + 31;
    /* 0x1df00 is a fill helper: it consumes g0/g1 as dimensions and
       takes its tile word from preserved g14, not a source pointer. */
    plan->source = mode == 0 ? 0 : 0x02fd0cd4;
    plan->tile = 19;
    plan->width = 2;
    plan->helper = mode == 0 ? 0x0001df00 : 0x0001dc90;
}
