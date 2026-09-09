/* Candidate packets recovered from i960 0x81b30-0x81ddc. */
#include "recovered_common.h"

struct recovered_geometry_candidate_packet_81b30_input {
    recovered_u32 candidate_cell0_integer;
    recovered_u32 candidate_cell2_integer;
    recovered_u32 related_plus8;
    recovered_u32 related_plus10;
};

struct recovered_geometry_candidate_packet_81b30_plan {
    recovered_u32 fifo_word[8];
    recovered_u32 fifo_count;
};

static recovered_u32 recovered_geometry_i960_subr(
    recovered_u32 source,
    recovered_u32 destination)
{
    /* i960 subr source,destination,result computes destination - source. */
    return destination - source;
}

void recovered_geometry_candidate_packet_81b30(
    const struct recovered_geometry_candidate_packet_81b30_input *input,
    struct recovered_geometry_candidate_packet_81b30_plan *plan)
{
    plan->fifo_word[0] = 10U;
    plan->fifo_word[1] = recovered_geometry_i960_subr(
        input->related_plus10, input->candidate_cell2_integer);
    plan->fifo_word[2] = recovered_geometry_i960_subr(
        input->candidate_cell0_integer, input->related_plus8);
    plan->fifo_word[3] = 62U; /* 31 + 31 */
    plan->fifo_word[4] = input->candidate_cell0_integer;
    plan->fifo_word[5] = input->candidate_cell0_integer;
    plan->fifo_word[6] = input->candidate_cell2_integer;
    plan->fifo_word[7] = input->related_plus10;
    plan->fifo_count = 8U;
}

struct recovered_geometry_followup_packet_81b30_plan {
    recovered_u32 fifo_word[6];
    recovered_u32 fifo_count;
};

void recovered_geometry_followup_packet_81b30(
    recovered_u32 selected_cell0_integer,
    recovered_u32 selected_cell2_integer,
    recovered_u32 selected_cell4_integer,
    recovered_u32 related_plus8,
    recovered_u32 related_plus10,
    recovered_u32 response_after_selector10,
    struct recovered_geometry_followup_packet_81b30_plan *plan)
{
    plan->fifo_word[0] = 10U;
    plan->fifo_word[1] = recovered_geometry_i960_subr(
        related_plus10, selected_cell2_integer);
    plan->fifo_word[2] = recovered_geometry_i960_subr(
        selected_cell0_integer, related_plus8);
    plan->fifo_word[3] = 29U;
    plan->fifo_word[4] = response_after_selector10 & 0xffffU;
    plan->fifo_word[5] = selected_cell4_integer;
    plan->fifo_count = 6U;
}

struct recovered_geometry_response_tail_81b30_plan {
    recovered_u32 fifo_word[14];
    recovered_u32 fifo_count;
};

void recovered_geometry_response_tail_81b30(
    recovered_u32 selected_cell0_integer,
    recovered_u32 selected_cell2_integer,
    recovered_u32 selected_cell4_integer,
    recovered_u32 object_plus8,
    recovered_u32 object_plus10,
    recovered_u32 response_after_selector10,
    recovered_u32 response_after_selector29,
    recovered_u32 response_after_selector30,
    struct recovered_geometry_response_tail_81b30_plan *plan)
{
    recovered_u32 difference_cell2 = recovered_geometry_i960_subr(
        object_plus10, selected_cell2_integer);
    recovered_u32 difference_cell0 = recovered_geometry_i960_subr(
        selected_cell0_integer, object_plus8);

    plan->fifo_word[0] = 10U;
    plan->fifo_word[1] = difference_cell2;
    plan->fifo_word[2] = difference_cell0;
    plan->fifo_word[3] = 29U;
    plan->fifo_word[4] = response_after_selector10 & 0xffffU;
    plan->fifo_word[5] = selected_cell4_integer;
    plan->fifo_word[6] = 30U;
    plan->fifo_word[7] = difference_cell0;
    plan->fifo_word[8] = selected_cell4_integer;
    plan->fifo_word[9] = 62U;
    plan->fifo_word[10] = recovered_geometry_i960_subr(
        response_after_selector29, selected_cell0_integer);
    plan->fifo_word[11] = object_plus8;
    plan->fifo_word[12] = response_after_selector30 + selected_cell2_integer;
    plan->fifo_word[13] = object_plus10;
    plan->fifo_count = 14U;
}

struct recovered_geometry_classifier_prefix_81d88_plan {
    recovered_u32 fifo_word[3];
    recovered_u32 fifo_count;
    recovered_u32 classifier_input;
    recovered_u32 classifier_target;
};

void recovered_geometry_classifier_prefix_81d88(
    recovered_u32 selected_cell0_integer,
    recovered_u32 selected_cell2_integer,
    recovered_u32 object_plus8,
    recovered_u32 object_plus10,
    recovered_u32 response_after_selector10,
    recovered_u32 object_plus184,
    struct recovered_geometry_classifier_prefix_81d88_plan *plan)
{
    recovered_u32 difference_cell2 = recovered_geometry_i960_subr(
        object_plus10, selected_cell2_integer);
    recovered_u32 difference_cell0 = recovered_geometry_i960_subr(
        selected_cell0_integer, object_plus8);
    int32_t response_halfword = recovered_sign_extend_16(
        response_after_selector10);
    int32_t object_halfword = recovered_sign_extend_16(object_plus184);

    plan->fifo_word[0] = 10U;
    plan->fifo_word[1] = difference_cell2;
    plan->fifo_word[2] = difference_cell0;
    plan->fifo_count = 3U;
    plan->classifier_input = (recovered_u32)(response_halfword - object_halfword);
    plan->classifier_target = 0x00073508U;
}

struct recovered_geometry_classifier_publication_81de0_plan {
    recovered_u32 result_table;
    recovered_u32 result_value;
    recovered_u32 action_destination;
    recovered_u32 action_value;
    recovered_u32 result_destination;
    recovered_u32 result_status;
    recovered_u32 phase_destination;
    recovered_u32 phase_value;
    recovered_u32 return_value;
};

void recovered_geometry_classifier_publication_81de0(
    recovered_u32 object_state,
    recovered_u32 response_passes_float_gate,
    recovered_u32 positive_result,
    recovered_u32 fallback_result,
    recovered_u32 preserved_phase,
    struct recovered_geometry_classifier_publication_81de0_plan *plan)
{
    const recovered_u32 positive_state = object_state == 2U ||
        object_state == 4U || object_state == 7U;

    if (positive_state != 0U && response_passes_float_gate != 0U) {
        plan->result_table = 0x00072780U;
        plan->result_value = positive_result;
        plan->action_value = 30U;
    } else {
        plan->result_table = 0x00072630U;
        plan->result_value = fallback_result;
        plan->action_value = 5U;
    }
    plan->action_destination = 0x00504db8U;
    plan->result_destination = 0x00504d94U;
    plan->result_status = 0U;
    plan->phase_destination = 0x00504d74U;
    plan->phase_value = preserved_phase;
    plan->return_value = 1U;
}

struct recovered_geometry_candidate_selection_81b30_plan {
    recovered_u32 candidate_present;
    recovered_u32 selected_cell_offset;
};

void recovered_geometry_candidate_selection_81b30(
    recovered_u32 best_index,
    struct recovered_geometry_candidate_selection_81b30_plan *plan)
{
    plan->candidate_present = best_index != 0xffffffffU ? 1U : 0U;
    plan->selected_cell_offset = best_index * 6U;
}

struct recovered_geometry_candidate_scan_cursor_81b30_plan {
    recovered_u32 candidate_valid;
    recovered_u32 candidate_count;
    recovered_u32 cell_offset;
    recovered_u32 field_offset[3];
};

void recovered_geometry_candidate_scan_cursor_81b30(
    recovered_u32 candidate_index,
    struct recovered_geometry_candidate_scan_cursor_81b30_plan *plan)
{
    plan->candidate_valid = candidate_index < 7U ? 1U : 0U;
    plan->candidate_count = 7U;
    plan->cell_offset = candidate_index * 6U;
    plan->field_offset[0] = 0U;
    plan->field_offset[1] = 2U;
    plan->field_offset[2] = 4U;
}
