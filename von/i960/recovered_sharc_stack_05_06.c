/* SHARC opcodes 0x05/0x06 affine-state stack discipline.
 *
 * Handler PCs from the dispatch table (SHARC 0x20000-based):
 * 0x05 -> 0x2016d advances a 12-word-copy push gated on
 * DM(0x30100) < 7; 0x06 -> 0x2018f rewinds DM(0x30101) by 12 on
 * nonzero depth, else returns. DM(0x30100) is zeroed and
 * DM(0x30101) set to 0x30200 at reset init.
 *
 * Live hardware probing
 * (von/build/probe_sharc_opcode_05_06.lua) shows pushes, pops,
 * an 8-deep overflow run, and a 9-deep drain run never change the
 * opcode-0x1a-observable state: every read matches the last 0x07
 * load. Exporters may therefore safely ignore 0x05/0x06 traffic.
 *
 * Push-copy addressing resolved by forced-FIFO marker probes: twelve
 * { R0 = DM(I7,M1); DM(M7,I7) = R0 } pairs with M7 = 11 slide the
 * record forward by exactly 12 (dest[k+12] = src[k], 0x30218+
 * untouched), so the M7 stores behave as displacement writes that
 * leave I7 walking +1 per read; I7 (saved to the pointer) ends 12
 * forward. A premodify walk would scatter to P+12,P+24,... while
 * reading back its own writes, which the snapshots refute. The
 * counter+1/pointer+12 saves are listing work (0x171-0x172,
 * 0x18d-0x18e): the attract-mode 08 stream resets both within frames
 * of any trial, so no post-trial snapshot can catch them -- only the
 * data move and the saturating guards are live-observable.
 */

typedef unsigned int u32;

#define STACK_DEPTH_MAX 7U

u32 sharc_stack_push_depth(u32 depth)
{
    return (depth >= STACK_DEPTH_MAX) ? STACK_DEPTH_MAX : depth + 1U;
}

typedef struct {
    u32 depth;
    u32 ptr;
} stack_push_out;

/* Full opcode-0x05 push: saturating depth gate, verbatim 12-word slide
 * of window[0..11] to window[12..23], pointer advance by 12. */
void sharc_stack_push_copy(u32 depth, u32 ptr, u32 window[24],
                           stack_push_out *o)
{
    unsigned i;
    if (depth >= STACK_DEPTH_MAX) {
        o->depth = depth;
        o->ptr = ptr;
        return;
    }
    for (i = 0; i < 12U; ++i)
        window[12U + i] = window[i];
    o->depth = depth + 1U;
    o->ptr = ptr + 12U;
}

typedef struct {
    u32 depth;
    u32 ptr;
} stack_pop_out;

void sharc_stack_pop(u32 depth, u32 ptr, stack_pop_out *o)
{
    if (depth == 0U) {
        o->depth = 0U;
        o->ptr = ptr;
        return;
    }
    o->depth = depth - 1U;
    o->ptr = ptr - 12U;
}
