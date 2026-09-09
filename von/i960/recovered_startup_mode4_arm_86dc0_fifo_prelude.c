/* Slot-20 FIFO prelude recovered from i960 0x86dc0-0x86ee8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 upload_call;
    recovered_u32 first_source, first_destination, first_bytes;
    recovered_u32 second_source, second_destination, second_bytes;
    recovered_u32 fifo_address;
    recovered_u32 fifo_word_count;
    recovered_u32 fifo_words[7];
    recovered_u32 response_source_address;
    recovered_u32 fifo_write_address;
    recovered_u32 fifo_write_count;
    recovered_u32 response_compare_value;
    recovered_u32 response_value;
    recovered_u32 value_503ad8, value_5040d8;
    recovered_u32 value_503ae0, value_5040e0;
    recovered_u32 response_match;
    recovered_u32 response_dispatch_target;
} recovered_startup_mode4_arm_result_86dc0_fifo_prelude;

int recovered_startup_mode4_arm_86dc0_fifo_prelude(
    recovered_u32 response_value,
    recovered_u32 value_503ad8,
    recovered_u32 value_5040d8,
    recovered_u32 value_503ae0,
    recovered_u32 value_5040e0,
    recovered_startup_mode4_arm_result_86dc0_fifo_prelude *result)
{
    recovered_startup_mode4_arm_result_86dc0_fifo_prelude r = {0};

    r.upload_call = 0xf5d40U;
    r.first_source = 0x51c9e0U;
    r.first_destination = 0x503ad0U;
    r.first_bytes = 0x600U;
    r.second_source = 0x51cfe0U;
    r.second_destination = 0x5040d0U;
    r.second_bytes = 0x600U;
    r.fifo_address = 0x884000U;
    r.fifo_word_count = 7U;
    r.fifo_words[0] = 31U;
    r.fifo_words[1] = value_503ad8;
    r.fifo_words[2] = value_5040d8;
    r.fifo_words[3] = 0U;
    r.fifo_words[4] = 0U;
    r.fifo_words[5] = value_503ae0;
    r.fifo_words[6] = value_5040e0;
    r.response_source_address = 0x51c9d0U;
    r.fifo_write_address = 0x884000U;
    r.fifo_write_count = r.fifo_word_count;
    r.response_compare_value = 1U;
    r.response_value = response_value;
    r.value_503ad8 = value_503ad8;
    r.value_5040d8 = value_5040d8;
    r.value_503ae0 = value_503ae0;
    r.value_5040e0 = value_5040e0;
    r.response_match = response_value == r.response_compare_value ? 1U : 0U;
    r.response_dispatch_target = r.response_match != 0U ? 0x86eecU : 0x873dcU;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
