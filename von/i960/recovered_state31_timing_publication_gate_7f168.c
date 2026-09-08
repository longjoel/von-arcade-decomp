/* State/timing publication gate recovered from i960 0x7f168-0x7f1f8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_timing_publication_gate_7f168_plan {
    u32 object_state;
    u32 related_state;
    u32 timing_below_40690000;
    u32 timing_gate_used;
    u32 direct_related_gate_passed;
    u32 related_object_gate_passed;
    u32 final_state_gate_passed;
    u32 publication_gate_passed;
    u32 target;
    u32 published_status;
    u32 failure_target;
};

void recovered_state31_timing_publication_gate_7f168(
    u32 object_state, u32 related_state, u32 timing_below_40690000,
    struct recovered_state31_timing_publication_gate_7f168_plan *plan)
{
    const u32 timing_passed = timing_below_40690000 ? 1U : 0U;
    const u32 direct_related = object_state != 0U && related_state == 2U;
    const u32 related_object = object_state == 3U && related_state == 7U;
    const u32 final_state = related_state != 6U || object_state != 5U;
    u32 uses_timing = 0U;
    u32 publication = 0U;

    /* The two cmprl arms are reached for (object=0, related=2), or for a
       nonzero object with related state 7 after the object=3 fast arm. */
    if (object_state == 0U && related_state == 2U)
        uses_timing = 1U;
    else if (object_state != 0U && related_state == 7U && object_state != 3U)
        uses_timing = 1U;

    if (direct_related || related_object)
        publication = 1U;
    else if (!uses_timing && object_state == 0U && related_state != 2U &&
             related_state != 7U)
        publication = 1U;
    else if (uses_timing && timing_passed)
        publication = 1U;

    if (publication && !final_state)
        publication = 0U;

    plan->object_state = object_state;
    plan->related_state = related_state;
    plan->timing_below_40690000 = timing_passed;
    plan->timing_gate_used = uses_timing;
    plan->direct_related_gate_passed = direct_related;
    plan->related_object_gate_passed = related_object;
    plan->final_state_gate_passed = final_state ? 1U : 0U;
    plan->publication_gate_passed = publication;
    plan->target = publication ? 0x0007f4acU : 0x0007f1f8U;
    plan->published_status = publication ? 7U : 0U;
    plan->failure_target = 0x0007f1f8U;
}
