/* MMIO doorbell recovered from i960 0x1ccf8-0x1cd0c.
 *
 * The leaf saves the caller link, then publishes g0 to the device
 * register at 0x1800000 with a halfword store (low 16 bits only) and
 * returns one-way through the saved link. Frequently called from the
 * service leaves with small constant arguments.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef uint16_t u16;

struct recovered_doorbell_plan {
    u32 reg_addr;
    u16 reg_stored;
    u32 link_saved;
};

void recovered_doorbell_plan(u32 value, u32 link,
                              struct recovered_doorbell_plan *plan)
{
    plan->reg_addr = 0x01800000U;
    /* stos keeps the low halfword of g0. */
    plan->reg_stored = (u16)(value & 0xFFFFU);
    /* mov g14,g1 ahead of bx(g1). */
    plan->link_saved = link;
}
