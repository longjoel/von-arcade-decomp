/* Secondary dual flag decoder recovered from i960 0x880c0-0x88100. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_flag_pair_880c0 {
    u32 flag_word_5024a4;
    u32 flag_word_50249c;
    u32 first_mask;
    u32 second_mask;
    u32 first_table_address;
    u32 second_table_address;
    u32 first_code;
    u32 second_code;
    u32 zero_code;
    u32 two_code;
    u32 four_code;
    u32 continuation;
};

struct recovered_stage_secondary_flag_pair_880c0
recovered_stage_secondary_flag_pair_880c0(u32 flag_word_5024a4,
                                          u32 flag_word_50249c,
                                          u32 first_mask,
                                          u32 second_mask)
{
    struct recovered_stage_secondary_flag_pair_880c0 out;

    out.flag_word_5024a4 = flag_word_5024a4;
    out.flag_word_50249c = flag_word_50249c;
    out.first_mask = first_mask;
    out.second_mask = second_mask;
    out.first_table_address = 0x00003d90U;
    out.second_table_address = 0x00003dc0U;
    out.zero_code = 0U;
    out.two_code = 2U;
    out.four_code = 4U;
    out.first_code = (flag_word_5024a4 & first_mask) != 0U ? out.two_code :
                     ((flag_word_50249c & first_mask) != 0U ? out.four_code : out.zero_code);
    out.second_code = (flag_word_5024a4 & second_mask) != 0U ? out.two_code :
                      ((flag_word_50249c & second_mask) != 0U ? out.four_code : out.zero_code);
    out.continuation = 0x00088100U;
    return out;
}
