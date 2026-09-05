/* Link-publish block recovered from i960 0x1ba08-0x1ba24.
 *
 * The block issues a caller-owned 0x2a4e0 sub-call with g0 = 2, then
 * publishes two constants: 1 to 0x5039f4 and the post-call resume
 * address (g14 = 0x1ba10, set by the call itself) to 0x503a00. Every
 * effect is constant, so the plan takes no inputs. Link/return
 * mechanics beyond the stored resume value stay caller-owned.
 */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_link_publish_plan {
    u32 call_arg;
    u32 flag_addr;
    u32 flag_value;
    u32 link_addr;
    u32 link_stored;
};

void recovered_link_publish_plan(struct recovered_link_publish_plan *plan)
{
    /* mov 2,g0 ahead of the 0x2a4e0 call. */
    plan->call_arg = 2U;
    /* mov 1,g1 then st g1,0x5039f4. */
    plan->flag_addr = 0x005039f4U;
    plan->flag_value = 1U;
    /* The call sets g14 to its resume address 0x1ba10, which the
     * following st publishes to 0x503a00. */
    plan->link_addr = 0x00503a00U;
    plan->link_stored = 0x0001ba10U;
}
