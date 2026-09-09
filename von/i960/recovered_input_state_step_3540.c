/* First deterministic state-update slice recovered from i960 0x3540-0x3580. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_input_state_step_3540 {
    u32 cleared_status_byte;
    u32 bit3_set;
    u32 next_state;
};

void recovered_input_state_step_3540(u32 packed_state, u32 status_byte,
                                     struct recovered_input_state_step_3540 *out)
{
    u32 state = packed_state;

    out->cleared_status_byte = 1U;
    out->bit3_set = (status_byte & 0x08U) != 0U ? 1U : 0U;
    if (out->bit3_set != 0U) {
        /* cmpibl 15,state branches only when state is greater than 15. */
        if (state <= 15U)
            ++state;
    } else {
        state = 0U;
    }
    out->next_state = state;
}

struct recovered_input_state_followup_3540 {
    u32 admission_passed;
    u32 timing_counter_incremented;
    u32 status_field_checked;
    u32 prior_field38;
    u32 field38_next;
    u32 field38_incremented;
    u32 field38_reset_to_nine;
    u32 field3c_incremented;
    u32 field_c4_cleared;
    u32 table_copy_called;
    u32 special_ready;
    u32 special_helper_called;
    u32 special_helper_argument;
    u32 status_f2_published;
    u32 field_c6_cleared;
};

/* Bounded continuation at 0x3584-0x3658. timing_value is the low halfword
 * stored at 0x5024c8; field38 is the byte at 0x1d00038. */
void recovered_input_state_followup_3540(
    u32 state, u32 timing_value, u32 status_34, u32 field38,
    struct recovered_input_state_followup_3540 *out)
{
    u32 admitted = state == 6U && timing_value <= 0x3ffU && status_34 == 0U;
    u32 next_field38 = field38;

    out->admission_passed = admitted;
    out->timing_counter_incremented = admitted;
    out->status_field_checked = admitted;
    out->prior_field38 = field38;
    out->field38_next = field38;
    out->field38_incremented = 0U;
    out->field38_reset_to_nine = 0U;
    out->field3c_incremented = 0U;
    out->field_c4_cleared = 0U;
    out->table_copy_called = 0U;
    out->special_ready = 0U;
    out->special_helper_called = 0U;
    out->special_helper_argument = 0x111bU;
    out->status_f2_published = 0U;
    out->field_c6_cleared = 0U;

    if (admitted) {
        ++next_field38;
        out->field38_incremented = 1U;
        if (next_field38 > 8U) {
            next_field38 = 9U;
            out->field38_reset_to_nine = 1U;
            out->field_c4_cleared = 1U;
        } else {
            out->field3c_incremented = 1U;
        }
        out->special_ready = field38 == 9U;
        out->table_copy_called = 1U;
        if (out->special_ready != 0U) {
            out->special_helper_called = 1U;
            out->status_f2_published = 1U;
            out->field_c6_cleared = 1U;
        }
    }
    out->field38_next = next_field38;
}

struct recovered_input_counter_gate_3658 {
    u32 status482_bit0_set;
    u32 c2_limit_passed;
    u32 c2_incremented;
    u32 c2_cleared;
    u32 c2_nonzero_checked;
    u32 status480_bit0_checked;
    u32 status480_bit0_set;
    u32 field40_incremented;
    u32 field_ce_incremented;
    u32 field_c8_cleared;
    u32 field36_threshold_branch;
    u32 field_c6_updated;
    u32 returned_to_3754;
};

/* Bounded counter gate at 0x3658-0x3754. Halfword arguments are passed as
 * their zero-extended values, matching the shlo16/shri16 normalization. */
void recovered_input_counter_gate_3658(
    u32 status482, u32 counter_c2, u32 status480, u32 field36,
    struct recovered_input_counter_gate_3658 *out)
{
    u32 bit0 = status482 & 1U;
    u32 c2_nonzero = counter_c2 != 0U;
    u32 threshold_branch = field36 <= 1U;

    out->status482_bit0_set = bit0 != 0U;
    out->c2_limit_passed = counter_c2 <= 0x3ffU;
    out->c2_incremented = bit0 != 0U && out->c2_limit_passed;
    out->c2_cleared = bit0 == 0U;
    out->c2_nonzero_checked = bit0 == 0U ? 1U : 0U;
    out->status480_bit0_checked = bit0 == 0U && c2_nonzero;
    out->status480_bit0_set = out->status480_bit0_checked &&
                              (status480 & 1U) != 0U;
    out->field40_incremented = out->status480_bit0_set;
    out->field_ce_incremented = out->status480_bit0_set;
    out->field_c8_cleared = out->status480_bit0_set;
    out->field36_threshold_branch = out->status480_bit0_set && threshold_branch;
    out->field_c6_updated = out->status480_bit0_set && !threshold_branch;
    out->returned_to_3754 = 1U;
}

struct recovered_input_counter_gate_3754 {
    u32 status482_bit1_set;
    u32 c0_limit_passed;
    u32 c0_incremented;
    u32 c0_cleared;
    u32 c0_nonzero_checked;
    u32 status480_bit1_checked;
    u32 status480_bit1_set;
    u32 field44_incremented;
    u32 field_ce_incremented;
    u32 field_c8_cleared;
    u32 field36_threshold_branch;
    u32 field_c6_updated;
    u32 g7_result;
    u32 returned_to_3884;
};

/* Bounded bit-1/counter gate at 0x3754-0x3884. */
void recovered_input_counter_gate_3754(
    u32 status482, u32 counter_c0, u32 status480, u32 field36,
    struct recovered_input_counter_gate_3754 *out)
{
    u32 bit1 = status482 & 2U;
    u32 counter_nonzero = counter_c0 != 0U;
    u32 threshold_branch = field36 <= 1U;
    u32 deep_path = bit1 == 0U && counter_nonzero && (status480 & 2U) != 0U;

    out->status482_bit1_set = bit1 != 0U;
    out->c0_limit_passed = counter_c0 <= 0x3ffU;
    out->c0_incremented = bit1 != 0U && out->c0_limit_passed;
    out->c0_cleared = bit1 == 0U;
    out->c0_nonzero_checked = bit1 == 0U ? 1U : 0U;
    out->status480_bit1_checked = bit1 == 0U && counter_nonzero;
    out->status480_bit1_set = deep_path;
    out->field44_incremented = deep_path;
    out->field_ce_incremented = deep_path;
    out->field_c8_cleared = deep_path;
    out->field36_threshold_branch = deep_path && threshold_branch;
    out->field_c6_updated = deep_path && !threshold_branch;
    out->g7_result = deep_path ? 1U : 0U;
    out->returned_to_3884 = 1U;
}
