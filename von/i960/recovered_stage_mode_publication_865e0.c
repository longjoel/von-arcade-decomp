/* Final mode publication stores recovered from i960 0x865e0-0x86620. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_mode_publication_865e0 {
    u32 previous_words[4];
    u32 previous_pair[2];
    u32 current_words[4];
    u32 current_pair[2];
    u32 active_words[4];
    u32 active_pair[2];
    u32 latch_509b80;
    u32 latch_509b84;
    u32 latch_509b88;
};

struct recovered_stage_mode_publication_865e0
recovered_stage_mode_publication_865e0(
    const u32 selected_words[4], const u32 selected_pair[2], u32 callback_g14)
{
    struct recovered_stage_mode_publication_865e0 out;
    u32 index;

    for (index = 0U; index < 4U; ++index) {
        out.previous_words[index] = selected_words[index];
        out.current_words[index] = selected_words[index];
        out.active_words[index] = selected_words[index];
    }
    for (index = 0U; index < 2U; ++index) {
        out.previous_pair[index] = selected_pair[index];
        out.current_pair[index] = selected_pair[index];
        out.active_pair[index] = selected_pair[index];
    }
    out.latch_509b80 = callback_g14;
    out.latch_509b84 = callback_g14;
    out.latch_509b88 = callback_g14;
    return out;
}
