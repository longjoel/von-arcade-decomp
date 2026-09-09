/* Math-window completion handoff from i960 0x8fddc-0x8fdf0. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_math_terminal_handoff_8fddc_input {
    recovered_u32 selected_window[4];
};

struct recovered_geometry_diagnostic_math_terminal_handoff_8fddc_plan {
    recovered_u32 window_address;
    recovered_u32 window_word[4];
    recovered_u32 completion_word;
    recovered_u32 next_packet_entry;
};

void recovered_geometry_diagnostic_math_terminal_handoff_8fddc(
    const struct recovered_geometry_diagnostic_math_terminal_handoff_8fddc_input *input,
    struct recovered_geometry_diagnostic_math_terminal_handoff_8fddc_plan *plan)
{
    plan->window_address = 0x804000U;
    plan->window_word[0] = input->selected_window[0];
    plan->window_word[1] = input->selected_window[1];
    plan->window_word[2] = input->selected_window[2];
    plan->window_word[3] = input->selected_window[3];
    plan->completion_word = 6U;
    plan->next_packet_entry = 0x8fdf0U;
}
