/* Controller clamp store recovered from i960 0x29c08-0x29c4c. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_clamp_store_plan {
    u32 value_addr;
    u32 zero_addr0;
    u32 zero_addr1;
    s32 clamp_max;
    s32 stored;
};

void recovered_clamp_store_plan(s32 value,
                                struct recovered_clamp_store_plan *plan)
{
    plan->value_addr = 0x0051a260U;
    plan->zero_addr0 = 0x0051a264U;
    plan->zero_addr1 = 0x0051a268U;
    plan->clamp_max = 0x100;
    /* Three-way signed clamp: bl takes the pre-setbit g5 floor of -256
     * when value < -256, the cmpible arm keeps values through 0x100,
     * and anything above stores the 0x100 ceiling. */
    if (value < -256)
        plan->stored = -256;
    else if (value > plan->clamp_max)
        plan->stored = plan->clamp_max;
    else
        plan->stored = value;
}
