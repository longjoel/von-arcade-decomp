/* Variant diagnostic response-window loop tail from i960 0x8ebb8-0x8ec84. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_variant_window_tail_8ebb8_input {
    recovered_u32 persistent_seed;
    recovered_u32 zero_window[3];
    recovered_u32 nonzero_window[3];
    recovered_u32 primary_cursor;
    recovered_u32 secondary_cursor;
};

struct recovered_geometry_diagnostic_variant_window_tail_8ebb8_plan {
    recovered_u32 selected_window[4];
    recovered_u32 control_address;
    recovered_u32 control_value;
    recovered_u32 completion_word;
    recovered_u32 next_primary_cursor;
    recovered_u32 next_secondary_cursor;
    recovered_u32 record_endpoint;
    recovered_u32 loop_continues;
    recovered_u32 continuation_entry;
};

void recovered_geometry_diagnostic_variant_window_tail_8ebb8(
    const struct recovered_geometry_diagnostic_variant_window_tail_8ebb8_input *input,
    struct recovered_geometry_diagnostic_variant_window_tail_8ebb8_plan *plan)
{
    const recovered_u32 *selected = input->persistent_seed != 0U ?
        input->nonzero_window : input->zero_window;
    plan->selected_window[0] = selected[0];
    plan->selected_window[1] = selected[1];
    plan->selected_window[2] = selected[2];
    plan->selected_window[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->completion_word = 6U;
    plan->next_primary_cursor = input->primary_cursor + 0x2cU;
    plan->next_secondary_cursor = input->secondary_cursor + 0x2cU;
    plan->record_endpoint = 0x142354U;
    plan->loop_continues = plan->next_primary_cursor <= plan->record_endpoint ? 1U : 0U;
    plan->continuation_entry = 0x8ea60U;
}
