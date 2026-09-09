/* Diagnostic-math setup bridge from i960 0x8f810-0x8f824. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_math_prologue_8f810_input {
    recovered_u32 persistent_seed;
    recovered_u32 saved_g12;
};

struct recovered_geometry_diagnostic_math_prologue_8f810_plan {
    recovered_u32 stack_adjust;
    recovered_u32 saved_register_address;
    recovered_u32 saved_g12_address;
    recovered_u32 saved_g12;
    recovered_u32 seed_address;
    recovered_u32 seed_word;
    recovered_u32 source_address;
    recovered_u32 source_entry;
};

void recovered_geometry_diagnostic_math_prologue_8f810(
    const struct recovered_geometry_diagnostic_math_prologue_8f810_input *input,
    struct recovered_geometry_diagnostic_math_prologue_8f810_plan *plan)
{
    plan->stack_adjust = 0xc0U;
    plan->saved_register_address = 0xe0U;
    plan->saved_g12_address = 0xf0U;
    plan->saved_g12 = input->saved_g12;
    plan->seed_address = 0x503b38U;
    plan->seed_word = input->persistent_seed;
    plan->source_address = 0x562b40U;
    plan->source_entry = 0x8f824U;
}
