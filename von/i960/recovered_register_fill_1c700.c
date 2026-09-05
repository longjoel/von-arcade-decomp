/* Register-fill schedule recovered from i960 0x1c700-0x1c72c.
 *
 * The leaf saves the caller link, clears its own link register, then
 * blank-fills exactly 4096 halfwords with zero at the caller-supplied
 * destination (setbit 12 countdown, body-first subo/stos/cmpi/bg, so
 * the loop performs the full setbit count of stores). Return goes
 * one-way through the saved link.
 */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_register_fill_plan {
    u32 iterations;
    u32 dst_end;
};

void recovered_register_fill_plan(u32 dst,
                                   struct recovered_register_fill_plan *plan)
{
    /* setbit 12,0,g4 fixes the trip count at 4096 zero stores. */
    plan->iterations = 4096U;
    plan->dst_end = dst + 4096U * 2U;
}
