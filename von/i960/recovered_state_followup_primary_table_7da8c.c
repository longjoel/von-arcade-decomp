/* Primary 24-entry follow-up table recovered from i960 0x7da8c. */
#include <stdint.h>

typedef uint32_t u32;

static const u32 targets[24] = {
    0x0007dbb8U, 0x0007dba8U, 0x0007dbb8U, 0x0007dba8U,
    0x0007daf0U, 0x0007dba8U, 0x0007dbb8U, 0x0007dba8U,
    0x0007daf0U, 0x0007db00U, 0x0007db1cU, 0x0007dbb8U,
    0x0007dba8U, 0x0007dbb8U, 0x0007dbc8U, 0x0007dbb8U,
    0x0007dba8U, 0x0007dbb8U, 0x0007dbc8U, 0x0007dbd8U,
    0x0007dbf4U, 0x0007dc04U, 0x0007db2cU, 0x0007dc98U,
};

u32 recovered_state_followup_primary_target_7da8c(u32 index)
{
    return index < 24U ? targets[index] : 0U;
}
