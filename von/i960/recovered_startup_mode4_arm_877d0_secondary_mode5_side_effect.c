/* Secondary response-4f path recovered from i960 0x877d0-0x8780c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode, flag, source_address, source_value, source_shifted;
    recovered_u32 mode_address, flag_address, shifted_address, buffer_address;
    recovered_u32 helper_call, continuation_target;
} recovered_startup_mode4_arm_result_877d0_secondary_mode5_side_effect;

int recovered_startup_mode4_arm_877d0_secondary_mode5_side_effect(
    recovered_u32 source_value,
    recovered_startup_mode4_arm_result_877d0_secondary_mode5_side_effect *result)
{
    recovered_startup_mode4_arm_result_877d0_secondary_mode5_side_effect r = {
        5U, 1U, 0x51c990U, source_value, source_value >> 8U,
        0x51c97cU, 0x51c9a0U, 0x51c994U, 0x503ad0U, 0x88a10U, 0x878d8U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
