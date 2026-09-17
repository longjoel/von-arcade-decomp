/* Pure 0x37130 frame-step dispatch core (i960 0x37350-0x37388).
 *
 * The 0x371e0 per-object frame step loads the signed halfword phase/state at
 * object+0x172, rejects the high bit (bbs 15, 0x37354) and any value above 42
 * (0x3735c-0x37368), then calls the non-null arm at 0x37130[state]
 * (0x37378-0x37388). The arm bodies are recovered separately; this core keeps
 * the gating and table selection host-testable by taking the table as input.
 *
 * Listing map:
 *   0x37350  ldos 0x172(r4),g4
 *   0x37354  bbs 15,g4,0x3738c        ; negative phase never dispatches
 *   0x3735c  lda 0x2a0000,g2
 *   0x37368  cmpibg g4,g2,0x3738c     ; state > 42 skips
 *   0x37378  ld 0x37130(g4),g1
 *   0x37380  cmpibe 0,g1,0x3738c      ; null entry skips
 *   0x37388  callx (g1)
 */

#include "recovered_framestate_dispatch.h"

recovered_framestate_u32 recovered_framestate_dispatch_core(
    volatile unsigned char *object,
    const recovered_framestate_arm *table,
    recovered_framestate_u32 count)
{
    recovered_framestate_u32 raw = (recovered_framestate_u32)
        *(volatile recovered_framestate_u16 *)(object + 0x172U);

    if ((raw & 0x8000U) != 0U)
        return 0U;
    if ((recovered_framestate_s32)(raw << 16) > 0x2a0000)
        return 0U;
    if (table == (const recovered_framestate_arm *)0 || raw >= count ||
        table[raw] == (recovered_framestate_arm)0)
        return 0U;
    return table[raw](object);
}
