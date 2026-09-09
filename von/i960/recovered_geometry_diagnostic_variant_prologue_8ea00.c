/* Sibling diagnostic setup bridge from i960 0x8ea00-0x8ea10. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_variant_prologue_8ea00_input {
    recovered_u32 persistent_seed;
};

struct recovered_geometry_diagnostic_variant_prologue_8ea00_plan {
    recovered_u32 stack_adjust;
    recovered_u32 saved_register_address;
    recovered_u32 seed_address;
    recovered_u32 seed_word;
    recovered_u32 packet_entry;
};

void recovered_geometry_diagnostic_variant_prologue_8ea00(
    const struct recovered_geometry_diagnostic_variant_prologue_8ea00_input *input,
    struct recovered_geometry_diagnostic_variant_prologue_8ea00_plan *plan)
{
    plan->stack_adjust = 0x80U;
    plan->saved_register_address = 0xb0U;
    plan->seed_address = 0x503b38U;
    plan->seed_word = input->persistent_seed;
    plan->packet_entry = 0x8ea10U;
}
