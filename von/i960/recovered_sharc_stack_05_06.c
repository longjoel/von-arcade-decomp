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
 * The push copy's exact addressing (M7/DAG update order) is
 * unresolved and excluded; only the depth discipline is modeled.
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
