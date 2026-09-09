/* Scheduler packet FIFO prelude recovered from i960 0x8459c-0x8467c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_packet_fifo_prelude_8459c {
    u32 fifo_word_count;
    u32 fifo_words[8];
    u32 record_field_06;
    u32 returned_word;
    u32 continues_8467c;
};

struct recovered_scheduler_packet_fifo_prelude_8459c
recovered_scheduler_packet_fifo_prelude_8459c(
    u32 table_value_for_g5, u32 object_field_08, u32 value_504e20,
    u32 object_field_10, u32 derived_difference_g6,
    u32 derived_difference_g4, u32 fifo_result, u32 record_g7)
{
    struct recovered_scheduler_packet_fifo_prelude_8459c out = {
        8U,
        {0xffffffffU, table_value_for_g5, object_field_08, value_504e20,
         object_field_10, 10U, derived_difference_g6,
         derived_difference_g4},
        record_g7, fifo_result & 0xffffU, 1U
    };
    return out;
}
