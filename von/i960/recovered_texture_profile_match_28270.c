/* Pure match predicate recovered from i960 routine 0x00028270. */

typedef unsigned int u32;

u32 recovered_texture_profile_match_28270(u32 table_word,
                                          u32 published_profile_word)
{
    return table_word == published_profile_word ? 1U : 0U;
}
