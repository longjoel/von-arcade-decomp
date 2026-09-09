/* Secondary slot-20 mode-entry stubs recovered from i960 0x87794/0x87844/0x8784c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 mode, continuation_target;
} recovered_startup_mode4_arm_result_secondary_mode_entry;

int recovered_startup_mode4_arm_secondary_mode_entry(
    recovered_u32 mode,
    recovered_startup_mode4_arm_result_secondary_mode_entry *result)
{
    recovered_startup_mode4_arm_result_secondary_mode_entry r = {mode, 0x87850U};
    return result != (void *)0 ? (*result = r, 1) : 1;
}
