/* Slot-20 response-0x4f wrapper recovered from i960 0x872d0-0x87308. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 response_handler;
    recovered_u32 register_5_value;
    recovered_u32 source_address, source_value;
    recovered_u32 register_4_value;
    recovered_u32 buffer_argument;
    recovered_u32 stored_mode_address, stored_mode_value;
    recovered_u32 stored_flag_address, stored_flag_value;
    recovered_u32 shifted_source_address, shifted_source_value;
    recovered_u32 side_effect_call, continuation_target;
} recovered_startup_mode4_arm_result_872d0_response4f;

int recovered_startup_mode4_arm_872d0_response4f(
    recovered_u32 source_value,
    recovered_startup_mode4_arm_result_872d0_response4f *result)
{
    recovered_startup_mode4_arm_result_872d0_response4f r = {0};

    r.response_handler = 0x4fU;
    r.register_5_value = 4U;
    r.source_address = 0x51c98cU;
    r.source_value = source_value;
    r.register_4_value = 1U;
    r.buffer_argument = 0x5040d0U;
    r.stored_mode_address = 0x51c97cU;
    r.stored_mode_value = 4U;
    r.stored_flag_address = 0x51c9a0U;
    r.stored_flag_value = 1U;
    r.shifted_source_address = 0x51c994U;
    r.shifted_source_value = source_value >> 8U;
    r.side_effect_call = 0x88a10U;
    r.continuation_target = 0x873ccU;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
