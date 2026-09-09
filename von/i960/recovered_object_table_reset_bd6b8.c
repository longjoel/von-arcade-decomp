/* Object table reset at i960 0xbd6b8. */
#include "recovered_common.h"

typedef struct {
    uint8_t object_table_200[32];
    recovered_u32 global_576ba0;
    recovered_u32 global_576ba4;
    recovered_u32 global_576ba8;
} recovered_object_table_reset_state_bd6b8;

/* The caller comparison is supplied as an explicit value: the original
 * compares object g0 with the fixed global at 0x503ad0. */
void recovered_object_table_reset_bd6b8(
    recovered_object_table_reset_state_bd6b8 *state,
    recovered_u32 object_pointer,
    recovered_u32 reference_503ad0)
{
    recovered_u32 index;
    for (index = 0U; index < 32U; ++index)
        state->object_table_200[index] = 0U;
    if (object_pointer == reference_503ad0)
        state->global_576ba0 = 0U;
    else
        state->global_576ba4 = 0U;
    state->global_576ba8 = 0U;
}
