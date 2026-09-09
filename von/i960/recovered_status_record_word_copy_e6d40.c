/* Status record halfword copy helper recovered from i960 0xe6d40-0xe6d78. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 halfword_count;
    recovered_u32 source_stride;
    recovered_u32 destination_stride;
    recovered_u32 source_load_width;
    recovered_u32 destination_store_width;
    recovered_u32 indirect_target;
    recovered_u32 return_target;
} recovered_status_record_word_copy_result_e6d40;

recovered_status_record_word_copy_result_e6d40
recovered_status_record_word_copy_plan_e6d40(void)
{
    recovered_status_record_word_copy_result_e6d40 result = {
        0x200U, 2U, 2U, 2U, 2U, 0x000e6d78U, 0x000e6d78U
    };
    return result;
}

void recovered_status_record_word_copy_e6d40(uint16_t *destination,
                                             const int16_t *source)
{
    recovered_u32 index;

    for (index = 0; index < 0x200U; ++index)
        destination[index] = (uint16_t)source[index];
}
