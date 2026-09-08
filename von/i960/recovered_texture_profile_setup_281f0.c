/* Pure setup/result contract recovered from i960 routine 0x000281f0. */

typedef unsigned int u32;

static const u32 texture_profile_source_table[5] = {
    0x02c77438U, 0x02cdbad3U, 0x02d594a1U, 0x02ddeffcU, 0x02e55c42U,
};

/* Bounded view of the five ROM words at 0x280c0; the i960 caller itself
 * indexes this table without a range check. */
u32 recovered_texture_profile_table_word_281f0(u32 index, u32 *out)
{
    if (index >= 5U)
        return 0U;
    *out = texture_profile_source_table[index];
    return 1U;
}

struct recovered_texture_profile_setup_281f0 {
    u32 profile_word;
    u32 saved_profile_address;
    u32 source_address;
    u32 primary_destination;
    u32 secondary_destination;
    u32 decoder_status;
    u32 state_a;
    u32 state_b;
    u32 saved_state_a;
    u32 saved_state_b;
};

void recovered_texture_profile_setup_281f0(
    u32 profile_word,
    u32 decoder_status,
    u32 prior_state_a,
    u32 prior_state_b,
    struct recovered_texture_profile_setup_281f0 *out)
{
    out->profile_word = profile_word;
    out->saved_profile_address = profile_word;
    out->source_address = profile_word;
    out->primary_destination = 0x11200000U;
    out->secondary_destination = 0x11000000U;
    out->decoder_status = decoder_status;
    out->state_a = prior_state_a;
    out->state_b = prior_state_b;
    out->saved_state_a = 0U;
    out->saved_state_b = 0U;

    if (decoder_status == 1U) {
        out->state_b = 29U;
    } else if (decoder_status == 2U) {
        out->saved_state_a = prior_state_a;
        out->saved_state_b = prior_state_b;
        out->state_a = 5U;
        out->state_b = 0U;
    }
}
