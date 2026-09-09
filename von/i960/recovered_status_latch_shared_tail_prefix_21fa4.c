/* Shared-tail prefix recovered from i960 0x21fa4-0x22018. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_shared_tail_prefix_route {
    RECOVERED_STATUS_LATCH_SHARED_TAIL_22108 = 0,
    RECOVERED_STATUS_LATCH_SHARED_TAIL_RENDER = 1,
    RECOVERED_STATUS_LATCH_SHARED_TAIL_CLEAR = 2
};

struct recovered_status_latch_shared_tail_prefix_plan {
    u32 route;
    u32 latch;
    u32 bit1_set;
    u32 helper;
    u32 source;
    u32 position_register;
    u32 position_offset;
    u32 continuation_target;
};

void recovered_status_latch_shared_tail_prefix_plan(
    int32_t latch, u32 bit1_set,
    struct recovered_status_latch_shared_tail_prefix_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_SHARED_TAIL_22108;
    plan->latch = (u32)latch;
    plan->bit1_set = bit1_set != 0U ? 1U : 0U;
    plan->helper = 0U;
    plan->source = 0U;
    plan->position_register = 0U;
    plan->position_offset = 0U;
    plan->continuation_target = 0x00022108U;

    /* g4 = latch - 36; cmpobg g4,119 sends latch >=156 to 0x22108. */
    if (latch >= 0 && latch <= 155) {
        plan->route = bit1_set != 0U
            ? RECOVERED_STATUS_LATCH_SHARED_TAIL_RENDER
            : RECOVERED_STATUS_LATCH_SHARED_TAIL_CLEAR;
        plan->helper = bit1_set != 0U ? 0x0001dc10U : 0x0001df00U;
        plan->source = bit1_set != 0U ? 0x02fe8ec2U : 0U;
        plan->position_register = 12U;
        plan->position_offset = 31U;
        plan->continuation_target = 0x0002201cU;
    }
}
