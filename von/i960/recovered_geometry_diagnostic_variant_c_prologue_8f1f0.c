/* Variant-C diagnostic setup bridge from i960 0x8f1f0-0x8f200. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_variant_c_prologue_8f1f0_input {
    recovered_u32 persistent_seed;
};

struct recovered_geometry_diagnostic_variant_c_prologue_8f1f0_plan {
    recovered_u32 stack_adjust;
    recovered_u32 saved_register_address;
    recovered_u32 seed_address;
    recovered_u32 seed_word;
    recovered_u32 packet_entry;
};

void recovered_geometry_diagnostic_variant_c_prologue_8f1f0(
    const struct recovered_geometry_diagnostic_variant_c_prologue_8f1f0_input *input,
    struct recovered_geometry_diagnostic_variant_c_prologue_8f1f0_plan *plan)
{
    plan->stack_adjust = 0x40U;
    plan->saved_register_address = 0x70U;
    plan->seed_address = 0x503b38U;
    plan->seed_word = input->persistent_seed;
    plan->packet_entry = 0x8f200U;
}
