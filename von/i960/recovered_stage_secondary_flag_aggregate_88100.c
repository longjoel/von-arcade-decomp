/* Secondary flag aggregation recovered from i960 0x88100-0x881a4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_flag_aggregate_88100 {
    u32 initial_first_code;
    u32 initial_second_code;
    u32 flag_word_5024a4;
    u32 flag_word_50249c;
    u32 mask_r6;
    u32 mask_r5;
    u32 mask_g2;
    u32 mask_g1;
    u32 counter_value;
    u32 counter_remainder;
    u32 row_offset;
    u32 final_first_code;
    u32 final_second_code;
    u32 first_store_address;
    u32 second_store_address;
    u32 continuation;
};

struct recovered_stage_secondary_flag_aggregate_88100
recovered_stage_secondary_flag_aggregate_88100(u32 initial_first_code,
                                               u32 initial_second_code,
                                               u32 flag_word_5024a4,
                                               u32 flag_word_50249c,
                                               u32 mask_r6,
                                               u32 mask_r5,
                                               u32 mask_g2,
                                               u32 mask_g1,
                                               u32 counter_value)
{
    struct recovered_stage_secondary_flag_aggregate_88100 out;

    out.initial_first_code = initial_first_code;
    out.initial_second_code = initial_second_code;
    out.flag_word_5024a4 = flag_word_5024a4;
    out.flag_word_50249c = flag_word_50249c;
    out.mask_r6 = mask_r6;
    out.mask_r5 = mask_r5;
    out.mask_g2 = mask_g2;
    out.mask_g1 = mask_g1;
    out.counter_value = counter_value;
    out.final_first_code = initial_first_code;
    out.final_second_code = initial_second_code;
    if ((flag_word_5024a4 & mask_r6) != 0U)
        out.final_first_code |= 1U << 4U;
    else if ((flag_word_50249c & mask_r5) != 0U)
        out.final_first_code |= 1U << 5U;
    if ((flag_word_5024a4 & mask_g2) != 0U)
        out.final_second_code |= 1U << 4U;
    else if ((flag_word_50249c & mask_g1) != 0U)
        out.final_second_code |= 1U << 5U;
    out.counter_remainder = counter_value % 120U;
    out.row_offset = out.counter_remainder * 12U;
    out.first_store_address = 0x005618f0U + out.row_offset + 4U;
    out.second_store_address = 0x005618f0U + out.row_offset + 8U;
    out.continuation = 0x000881a4U;
    return out;
}
