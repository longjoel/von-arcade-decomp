/* Slot-20 secondary setup wrapper recovered from i960 0x87844-0x87864. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode, source_address, source_value;
    recovered_u32 flag, buffer_address, continuation_target;
} recovered_startup_mode4_arm_result_87850_shared_setup;

int recovered_startup_mode4_arm_87850_shared_setup(
    recovered_u32 mode, recovered_u32 source_value,
    recovered_startup_mode4_arm_result_87850_shared_setup *result)
{
    recovered_startup_mode4_arm_result_87850_shared_setup r = {
        mode, 0x51c990U, source_value, 1U, 0x503ad0U, 0x87864U
    };
    return result != (void *)0 ? (*result = r, 1) : 1;
}
