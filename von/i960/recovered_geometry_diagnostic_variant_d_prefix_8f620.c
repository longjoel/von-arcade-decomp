/* Variant-D prefix bridge from i960 0x8f620-0x8f634. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_variant_d_prefix_8f620_input {
    recovered_u32 persistent_seed;
};

struct recovered_geometry_diagnostic_variant_d_prefix_8f620_plan {
    recovered_u32 seed_address;
    recovered_u32 seed_word;
    recovered_u32 first_fifo_word;
    recovered_u32 packet_body_entry;
};

void recovered_geometry_diagnostic_variant_d_prefix_8f620(
    const struct recovered_geometry_diagnostic_variant_d_prefix_8f620_input *input,
    struct recovered_geometry_diagnostic_variant_d_prefix_8f620_plan *plan)
{
    plan->seed_address = 0x503b38U;
    plan->seed_word = input->persistent_seed;
    plan->first_fifo_word = 5U;
    plan->packet_body_entry = 0x8f634U;
}
