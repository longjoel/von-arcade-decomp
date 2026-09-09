/* Deterministic setup prefix recovered from i960 0x7ff40-0x7ffcc. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_command_prefix_7ff40_plan {
    u32 object_base;
    u32 selector;
    u32 object_table_base;
    u32 object_byte_address;
    u32 selected_object_byte;
    u32 reduced_profile;
    u32 profile_index;
    u32 profile_table_base;
    u32 profile_record_address;
    u32 profile_record_plus4;
    u32 profile_sum;
    u32 profile_scalar_bits;
    u32 profile_scalar_source;
    u32 profile_record_plus48;
    u32 profile_record_plus56;
    u32 initial_command;
    u32 fifo_destination;
};

/*
 * The caller's object field at +0x74 is a pointer to the byte table.  The
 * selected byte is addressed with selector*32.  The ROM keeps the selected
 * byte in r8 for the profile-table index, while separately using signed
 * (selected_byte - 1) rem 6 in g4 for later packet/state selection.  This
 * helper reports addresses and raw values; it deliberately
 * leaves the i960 floating multiply and subsequent FIFO packet words to the
 * later packet-builder model.
 */
void recovered_geometry_command_prefix_7ff40(
    u32 object_base,
    u32 selector,
    u32 object_field_74,
    u32 object_byte_value,
    u32 profile_table_base,
    u32 profile_word_0,
    u32 profile_word_4,
    u32 profile_word_12,
    u32 profile_word_14,
    struct recovered_geometry_command_prefix_7ff40_plan *plan)
{
    const u32 object_table_base = object_field_74 + 0x200U;
    const u32 object_byte_address = object_table_base + (selector << 5U);
    const u32 selected_object_byte = object_byte_value & 0xffU;
    const int32_t reduced_profile_signed =
        ((int32_t)selected_object_byte - 1) % 6;
    const u32 reduced_profile = (u32)reduced_profile_signed;
    const u32 profile_index = selected_object_byte;
    const u32 profile_record_address =
        profile_table_base + (profile_index * 48U);

    plan->object_base = object_base;
    plan->selector = selector;
    plan->object_table_base = object_table_base;
    plan->object_byte_address = object_byte_address;
    plan->selected_object_byte = selected_object_byte;
    plan->reduced_profile = reduced_profile;
    plan->profile_index = profile_index;
    plan->profile_table_base = profile_table_base;
    plan->profile_record_address = profile_record_address;
    plan->profile_record_plus4 = profile_word_4;
    plan->profile_sum = profile_word_0 + profile_word_4;
    plan->profile_scalar_bits = 0x41200000U;
    plan->profile_scalar_source = profile_word_12;
    plan->profile_record_plus48 = profile_word_12;
    plan->profile_record_plus56 = profile_word_14;
    plan->initial_command = 30U;
    plan->fifo_destination = 0x00884000U;
}
