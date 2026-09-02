/* Full-plane clear thunks recovered from i960 0x22c70-0x22ce4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_plane_full_clear_plan {
    u32 destination;
    u32 word_count;
    u32 value;
    u32 return_stub;
    u32 fill_register_after_return;
};

void recovered_plane_full_clear_plan(u32 variant,
                                     struct recovered_plane_full_clear_plan *plan)
{
    plan->destination = variant == 0U ? 0x01000000U : 0x01004000U;
    plan->word_count = 0xfffU;
    plan->value = 0U;
    plan->return_stub = variant == 0U ? 0x00022ca4U : 0x00022ce4U;
    plan->fill_register_after_return = 0U;
}
