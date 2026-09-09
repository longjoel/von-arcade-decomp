/* Bounded strip handoff recovered from i960 0x21cf8-0x21d40. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_strip_route {
    RECOVERED_STATUS_LATCH_STRIP = 0,
    RECOVERED_STATUS_LATCH_STRIP_DOWNSTREAM = 1
};

struct recovered_status_latch_strip_handoff_plan {
    u32 route;
    u32 strip_builder;
    u32 column;
    u32 row;
    u32 input;
    u32 width;
    u32 scale;
    u32 first_value;
    u32 second_value;
    u32 third_value;
    u32 fill_value;
    u32 continuation_target;
    u32 downstream_target;
};

void recovered_status_latch_strip_handoff_plan(
    int32_t latch, struct recovered_status_latch_strip_handoff_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_STRIP_DOWNSTREAM;
    plan->strip_builder = 0U;
    plan->column = 0U;
    plan->row = 0U;
    plan->input = 0U;
    plan->width = 0U;
    plan->scale = 0U;
    plan->first_value = 0U;
    plan->second_value = 0U;
    plan->third_value = 0U;
    plan->fill_value = 0U;
    plan->continuation_target = 0U;
    plan->downstream_target = 0x00021d44U;

    /* cmpibg r6, latch+31, 0x21d44 selects the strip for latch <= 50. */
    if (latch <= 50) {
        plan->route = RECOVERED_STATUS_LATCH_STRIP;
        plan->strip_builder = 0x00020a20U;
        plan->column = 7U;
        plan->row = 8U;
        plan->input = 1U;
        plan->width = 0x118U;
        plan->scale = 0x118U;
        plan->continuation_target = 0x00021fa4U;
    }
}
