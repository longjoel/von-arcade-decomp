/* Bounded record/text routes recovered from i960 0x21af0-0x21cf4. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_record_route {
    RECOVERED_STATUS_LATCH_PLAIN_RECORDS = 0,
    RECOVERED_STATUS_LATCH_SHARED_TAIL = 1,
    RECOVERED_STATUS_LATCH_ATTRIBUTED_RECORDS = 2,
    RECOVERED_STATUS_LATCH_DOWNSTREAM = 3
};

struct recovered_status_latch_record_route_plan {
    u32 route;
    u32 record_dispatch;
    u32 record_mode;
    u32 text_helper;
    u32 text_call_count;
    u32 downstream_target;
};

void recovered_status_latch_record_route_plan(int32_t latch,
                                              struct recovered_status_latch_record_route_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_DOWNSTREAM;
    plan->record_dispatch = 0U;
    plan->record_mode = 0U;
    plan->text_helper = 0U;
    plan->text_call_count = 0U;
    plan->downstream_target = 0x00021cf8U;

    if (latch >= 34 && latch <= 35) {
        plan->route = RECOVERED_STATUS_LATCH_PLAIN_RECORDS;
        plan->record_dispatch = 0x000211f0U;
        plan->record_mode = 0U;
        plan->text_helper = 0x0001d250U;
        plan->text_call_count = 3U;
    } else if (latch == 36) {
        plan->route = RECOVERED_STATUS_LATCH_SHARED_TAIL;
        plan->downstream_target = 0x00021fa4U;
    } else if (latch >= 37 && latch <= 48) {
        plan->route = RECOVERED_STATUS_LATCH_ATTRIBUTED_RECORDS;
        plan->record_dispatch = 0x000211f0U;
        plan->record_mode = 1U;
        plan->text_helper = 0x0001d210U;
        plan->text_call_count = 3U;
    }
}
