/* Masked call dispatch recovered from i960 0x1bafc-0x1bb4c.
 *
 * The block masks the service counter at 0x503a04 to six bits and
 * dispatches on the result, then always bumps the counter in place:
 * a zero mask issues caller-owned 0x1ffb0 (with 1) and 0x2a4e0 (with
 * 0x1342) sub-calls, a 32 mask issues 0x1ffb0 (with 0) alone, and any
 * other mask performs the bump with no calls. Sub-call bodies stay
 * caller-owned.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_masked_call_plan {
    u32 counter_addr;
    u32 masked;
    s32 dual_call;
    s32 single_call;
    u32 first_call_arg;
    u32 second_call_arg;
    u32 bumped_counter;
};

void recovered_masked_call_plan(u32 counter,
                                 struct recovered_masked_call_plan *plan)
{
    plan->counter_addr = 0x00503a04U;
    /* lda 0x3f,g1 then and: six-bit mask. */
    plan->masked = counter & 0x3fU;
    plan->dual_call = plan->masked == 0U ? 1 : 0;
    plan->single_call = plan->masked == 32U ? 1 : 0;
    /* mov 1,g0 / mov 0,g0 ahead of the 0x1ffb0 calls. */
    plan->first_call_arg = plan->dual_call ? 1U : 0U;
    /* lda 0x1342,g0 ahead of the 0x2a4e0 call. */
    plan->second_call_arg = 0x1342U;
    /* ld/addo/st: the counter always bumps by one. */
    plan->bumped_counter = counter + 1U;
}
