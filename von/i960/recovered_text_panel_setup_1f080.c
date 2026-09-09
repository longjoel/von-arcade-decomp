/* Current-origin text panel route recovered from i960 0x1f080-0x1f0cc. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_text_panel_setup_plan {
    u32 timing_cdc;
    u32 timing_ce0;
    u32 timing_ce4;
    u32 helper;
    u32 source;
    u32 width;
    u32 rows;
};

void recovered_text_panel_setup_1f080_plan(
    u32 source_present, u32 caller_g9,
    struct recovered_text_panel_setup_plan *plan)
{
    plan->timing_cdc = 19U;
    plan->timing_ce0 = 19U;
    plan->timing_ce4 = caller_g9 + 31U;
    plan->helper = source_present ? 0x0001dc90U : 0x0001df00U;
    plan->source = source_present ? 0x02fe077eU : 0U;
    plan->width = 23U;
    plan->rows = 5U;
}
