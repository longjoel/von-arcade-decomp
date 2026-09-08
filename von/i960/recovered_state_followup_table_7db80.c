/* Follow-up handler table recovered from i960 0x7db80-0x7dba8. */
#include <stdint.h>

typedef uint32_t u32;

u32 recovered_state_followup_target_7db80(u32 index)
{
    static const u32 targets[10] = {
        0x0007dba8U, 0x0007dba8U, 0x0007dbb8U, 0x0007dbb8U,
        0x0007dbc8U, 0x0007dbd8U, 0x0007dbf4U, 0x0007dc04U,
        0x0007dc98U, 0x0007dca8U,
    };

    return index < 10U ? targets[index] : 0U;
}
