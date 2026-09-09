/* Tile-plane clear thunks recovered from i960 0x22c70-0x22d24. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_plane_full_clear_plan {
    u32 wrapper_entry;
    u32 body_entry;
    u32 destination;
    u32 word_count;
    u32 value;
    u32 return_stub;
    u32 body_uses_caller_link;
    u32 fill_register_after_return;
};

void recovered_plane_full_clear_plan(u32 variant,
                                     struct recovered_plane_full_clear_plan *plan)
{
    plan->wrapper_entry = variant == 0U ? 0x00022c70U
        : variant == 1U ? 0x00022cb0U : 0x00022cf0U;
    plan->body_entry = variant == 0U ? 0x00022c78U
        : variant == 1U ? 0x00022cb8U : 0x00022cf8U;
    plan->destination = variant == 0U ? 0x01000000U
        : variant == 1U ? 0x01004000U : 0x01001280U;
    /* The third sibling seeds g4 with 31+31, then pre-decrements it. */
    plan->word_count = variant == 2U ? 61U : 0xfffU;
    plan->value = 0U;
    plan->return_stub = variant == 0U ? 0x00022ca4U
        : variant == 1U ? 0x00022ce4U : 0x00022d24U;
    /* At the body entry, bal supplies the bx(g0) target; the wrapper first
     * replaces that link with the local stub above. */
    plan->body_uses_caller_link = 1U;
    plan->fill_register_after_return = 0U;
}
