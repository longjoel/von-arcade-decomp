/* Exact pre-refinement scalar formed by SHARC opcode 0x4d at 0x20d04-0x20d08. */
#include <stdint.h>

float recovered_sharc_opcode_4d_horizontal_seed(float dx, float dz)
{
    /* d05 copies F2 (already dz) into F4; d06 therefore computes dz*dz. */
    return dx * dx + dz * dz;
}
