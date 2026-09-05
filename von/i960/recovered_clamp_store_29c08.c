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
    /* The bl/cmpible pair reduces to a signed minimum: values below
     * -256 keep the entry value, anything above 0x100 stores 0x100. */
    plan->stored = value > plan->clamp_max ? plan->clamp_max : value;
}
