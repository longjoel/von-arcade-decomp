/* Service head block recovered from i960 0x1ba30-0x1ba6c.
 *
 * The block issues caller-owned sub-calls in order — 0x1c618 with the
 * entry registers, 0x1ccf8 with g0 = 0, 0x2a4e0 with g0 = 0x1013,
 * then 0x1fa00 — before its pure store effects: preset 0x12c to
 * 0x503a04 and bump the word at 0x503a00 by one. Only the stores and
 * the outbound call arguments belong to this schedule; sub-call
 * bodies and entry-register contents stay caller-owned.
 */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_service_head_plan {
    u32 setup_call_arg;
    u32 profile_call_arg;
    u32 preset_addr;
    u32 preset_value;
    u32 bump_addr;
    u32 bumped_value;
};

void recovered_service_head_plan(u32 bump_base,
                                  struct recovered_service_head_plan *plan)
{
    /* mov 0,g0 ahead of bal 0x1ccf8. */
    plan->setup_call_arg = 0U;
    /* lda 0x1013,g0 ahead of call 0x2a4e0 (and 0x1fa00). */
    plan->profile_call_arg = 0x1013U;
    /* lda 0x12c,g1 then st g1,0x503a04. */
    plan->preset_addr = 0x00503a04U;
    plan->preset_value = 0x12cU;
    /* ld/addo/st: the word at 0x503a00 bumps by one. */
    plan->bump_addr = 0x00503a00U;
    plan->bumped_value = bump_base + 1U;
}
