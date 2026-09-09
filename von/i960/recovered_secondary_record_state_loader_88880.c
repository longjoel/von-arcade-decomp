/* Shared record-state loader recovered from i960 0x88880-0x888e8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_secondary_record_state_loader_88880 {
    u32 phase_value;
    u32 record_word_30;
    u32 record_halfword_48;
    u32 linked_record_halfword_48;
    u32 record_halfword_1d6;
    u32 phase_required;
    u32 record_gate_address;
    u32 state_51c98c;
    u32 state_51c990;
    u32 argument_861e8;
    u32 helper_target;
    u32 loaded_any_state;
    u32 accepted;
};

struct recovered_secondary_record_state_loader_88880
recovered_secondary_record_state_loader_88880(
    u32 phase_value, u32 record_word_30, u32 record_halfword_48,
    u32 linked_record_halfword_48, u32 record_halfword_1d6)
{
    struct recovered_secondary_record_state_loader_88880 out;
    u32 first_state = record_halfword_48 & 0xffffU;
    u32 linked_state = linked_record_halfword_48 & 0xffffU;

    out.phase_value = phase_value;
    out.record_word_30 = record_word_30;
    out.record_halfword_48 = record_halfword_48;
    out.linked_record_halfword_48 = linked_record_halfword_48;
    out.record_halfword_1d6 = record_halfword_1d6;
    out.phase_required = 10U;
    out.record_gate_address = 0x30U;
    out.state_51c98c = 0U;
    out.state_51c990 = 0U;
    out.argument_861e8 = 0U;
    out.helper_target = 0x000861e8U;
    out.loaded_any_state = 0U;
    out.accepted = phase_value == out.phase_required && record_word_30 == 0U ? 1U : 0U;
    if (out.accepted != 0U) {
        if (first_state != 0U) {
            out.state_51c98c = first_state;
            out.loaded_any_state = 1U;
        }
        if (linked_state != 0U)
            out.state_51c990 = linked_state;
        out.argument_861e8 = record_halfword_1d6 & 0xffffU;
    }
    return out;
}
