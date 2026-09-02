/* Plan recovered from i960 0x20ae0-0x20b48. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_hardware_strip_clear_plan {
    u32 destination;
    u32 word_count;
    u32 value;
    u32 return_stub;
    u32 fill_register_after_return;
};

void recovered_hardware_strip_clear_plan(u32 mode,
                                         struct recovered_hardware_strip_clear_plan *plan)
{
    plan->destination = 0x0100d000U;
    plan->word_count = 0x5ffU;
    plan->value = mode != 0U ? 0xffffU : 0U;
    plan->return_stub = 0x00020b48U;
    plan->fill_register_after_return = 0U;
}
