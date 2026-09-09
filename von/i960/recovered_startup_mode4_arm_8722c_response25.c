/* Slot-20 response-0x25 wrapper recovered from i960 0x8722c-0x87244. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 response_handler;
    recovered_u32 register_5_value;
    recovered_u32 source_address, source_value;
    recovered_u32 register_4_value;
    recovered_u32 buffer_argument;
    recovered_u32 continuation_target;
} recovered_startup_mode4_arm_result_8722c_response25;

int recovered_startup_mode4_arm_8722c_response25(
    recovered_u32 source_value,
    recovered_startup_mode4_arm_result_8722c_response25 *result)
{
    recovered_startup_mode4_arm_result_8722c_response25 r = {0};

    r.response_handler = 0x25U;
    r.register_5_value = 10U;
    r.source_address = 0x51c98cU;
    r.source_value = source_value;
    r.register_4_value = 1U;
    r.buffer_argument = 0x5040d0U;
    r.continuation_target = 0x87738U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
