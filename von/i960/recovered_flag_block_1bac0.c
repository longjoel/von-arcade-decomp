/* Conditional flag block recovered from i960 0x1bac0-0x1baf8.
 *
 * The block compares the service counter at 0x503a04 against 0x118
 * and rejoins at 0x1bafc when different. On equality it issues a
 * caller-owned 0x1c618 sub-call, stores 7 to 0x503a00, and clears bit
 * 0 of the halfword device register at 0x10000000 (read, and 0xfffe,
 * write back). Only the compare select, the constant stores, and the
 * mask belong to this schedule; the sub-call body and the live
 * register contents stay caller-owned.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;
typedef uint16_t u16;

struct recovered_flag_block_plan {
    u32 counter_addr;
    s32 took_branch;
    u32 flag_addr;
    u32 flag_value;
    u32 reg_addr;
    u16 reg_mask;
    u16 reg_stored;
};

void recovered_flag_block_plan(u32 counter, u16 reg_value,
                                struct recovered_flag_block_plan *plan)
{
    plan->counter_addr = 0x00503a04U;
    /* cmpibne g4,g1,0x1bafc: the body runs only on equality. */
    plan->took_branch = counter == 0x118U ? 1 : 0;
    /* mov 7,g1 then st g1,0x503a00. */
    plan->flag_addr = 0x00503a00U;
    plan->flag_value = 7U;
    /* lda 0xfffe,g1 then and/stos: clear bit 0, keep the rest. */
    plan->reg_addr = 0x10000000U;
    plan->reg_mask = 0xFFFEU;
    plan->reg_stored = (u16)(reg_value & 0xFFFEU);
}
