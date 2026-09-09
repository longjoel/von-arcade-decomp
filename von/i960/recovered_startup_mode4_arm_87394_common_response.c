/* Shared slot-20 response continuation recovered from i960 0x87394-0x873d8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 register_5_value;
    recovered_u32 source_address, source_value;
    recovered_u32 register_4_value;
    recovered_u32 mode_address, mode_value;
    recovered_u32 flag_address, flag_value;
    recovered_u32 shifted_source_address, shifted_source_value;
    recovered_u32 first_helper_call;
    recovered_u32 buffer_address;
    recovered_u32 second_helper_call;
    recovered_u32 continuation_target;
} recovered_startup_mode4_arm_result_87394_common_response;

int recovered_startup_mode4_arm_87394_common_response(
    recovered_u32 source_value,
    recovered_startup_mode4_arm_result_87394_common_response *result)
{
    recovered_startup_mode4_arm_result_87394_common_response r = {0};

    r.register_5_value = 4U;
    r.source_address = 0x51c98cU;
    r.source_value = source_value;
    r.register_4_value = 1U;
    r.mode_address = 0x51c97cU;
    r.mode_value = 4U;
    r.flag_address = 0x51c9a0U;
    r.flag_value = 1U;
    r.shifted_source_address = 0x51c994U;
    r.shifted_source_value = source_value >> 8U;
    r.first_helper_call = 0x888f0U;
    r.buffer_address = 0x503ad0U;
    r.second_helper_call = 0x88af0U;
    r.continuation_target = 0x878f8U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
