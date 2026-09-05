/* Service-slot forward leaf recovered from i960 0x1b940-0x1b95c.
 *
 * The leaf copies the service halfword at 0x503a80 to 0x5032f4
 * (ldos/stos preserves the bit pattern), then issues two caller-owned
 * sub-calls that stay outside this pure schedule: 0x1fe90 receives the
 * sign-extended halfword in g4, and 0x2a4e0 receives g0 = 3.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;
typedef uint16_t u16;

struct recovered_slot_forward_plan {
    u32 copy_src_addr;
    u32 copy_dst_addr;
    u16 copy_value;
    s32 call0_arg;
    u32 call1_arg;
};

void recovered_slot_forward_plan(u16 raw_halfword,
                                  struct recovered_slot_forward_plan *plan)
{
    plan->copy_src_addr = 0x00503a80U;
    plan->copy_dst_addr = 0x005032f4U;
    plan->copy_value = raw_halfword;
    /* ldos sign-extends the halfword into g4 for the 0x1fe90 call. */
    plan->call0_arg = (s32)(int16_t)raw_halfword;
    /* mov 3,g0 ahead of the 0x2a4e0 call. */
    plan->call1_arg = 3U;
}
