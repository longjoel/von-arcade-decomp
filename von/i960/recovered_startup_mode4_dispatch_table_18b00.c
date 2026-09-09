/* Startup mode-4 dispatch table recovered from i960 0x18b00-0x18c00. */
#include "recovered_common.h"

int recovered_startup_mode4_dispatch_table_18b00(recovered_u32 table[64])
{
    static const recovered_u32 entries[64] = {
        0x18c00U, 0x18da0U, 0x19030U, 0x0ce670U, 0x0ce8f0U, 0x19660U,
        0x196c0U, 0x19830U, 0x19c30U, 0x1a280U, 0x1a4a0U, 0x1afe0U,
        0x1b470U, 0x95910U, 0x99c70U, 0x1b960U, 0x1b9d0U, 0x1ba30U,
        0x1ba70U, 0x86dc0U, 0x87ac0U, 0x86a90U, 0xe4250U, 0xe4ae0U,
        0xe5650U, 0xe4720U, 0x1b980U, 0x1bac0U, 0xd3860U, 0xd3960U,
        0xd3990U, 0xd5eb0U, 0xdc2b0U, 0xdc3f0U, 0xdc6d0U, 0U,
        0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U,
        0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U,
        0U, 0U, 0U, 0U
    };
    if (table == (void *)0)
        return 0;
    for (recovered_u32 i = 0; i < 64U; ++i)
        table[i] = entries[i];
    return 1;
}
