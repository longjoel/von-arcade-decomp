/* Table-dispatched geometry FIFO packet, i960 routines
 * 0x00090c10-0x00090d44, 0x00090d50-0x00090e74, 0x00090e80-0x00090fa8.
 *
 * The three routines share one template and differ only in a single
 * packet constant (0x90c10: 0xb800; 0x90d50: 3 << 14 = 0xc000;
 * 0x90e80: 0xc800), which arrives here as a value, so one model
 * covers all three.
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst. Emits a 14-word
 * packet to the host FIFO at 0x884000:
 *   w = [5, 18, 0x40e00000, 0x41800000, g14, 21, site, 19,
 *        0x40400000 x3, 58 (addo 31,27), [0x802008], 6].
 * Around the packet, MMIO moves [0x802008]+0x34 to [0x801008]; those
 * transports stay outside this contract, and [0x802008] arrives as
 * an input.
 * The g0 payload is reduced by `remi 30` (modeled as unsigned
 * modulo; callers build g0 from RAM bit tests), then tripled for a
 * 12-byte entry fetch from the ROM table at 0x2be52b0 (30 entries;
 * table bundled below, read live via von/build/probe_dispatch_table.lua):
 * entry = {ptr, same, value}. When [ptr] is zero the control-register
 * block is skipped; otherwise [0x800010] = 0x101, [0x804000] = [ptr],
 * [0x804004] = entry[1], [0x804008] = entry[2], [0x80400c] = 0.
 * Entry 0 is the all-zero ROM entry, so index 0 always skips.
 */

typedef unsigned int u32;

#define DISPATCH_PACKET_WORDS 14U
#define DISPATCH_TABLE_COUNT 30U
#define DISPATCH_SITE_90C10 0xb800U
#define DISPATCH_SITE_90D50 0xc000U
#define DISPATCH_SITE_90E80 0xc800U

static const u32 dispatch_table[DISPATCH_TABLE_COUNT][3] = {
    {0x00000000U, 0x00000000U, 0x00000000U},
    {0x00400c54U, 0x00400c54U, 0x0084695eU},
    {0x00400c58U, 0x00400c58U, 0x00846ccbU},
    {0x00400c5cU, 0x00400c5cU, 0x00847038U},
    {0x00400c60U, 0x00400c60U, 0x008473a5U},
    {0x00400c64U, 0x00400c64U, 0x00847712U},
    {0x00400c68U, 0x00400c68U, 0x00847a7fU},
    {0x00400c6cU, 0x00400c6cU, 0x00847decU},
    {0x00400c70U, 0x00400c70U, 0x00848159U},
    {0x00400c74U, 0x00400c74U, 0x008484c6U},
    {0x00400c78U, 0x00400c78U, 0x00848833U},
    {0x00400c7cU, 0x00400c7cU, 0x00848ba0U},
    {0x00400c80U, 0x00400c80U, 0x00848f0dU},
    {0x00400c84U, 0x00400c84U, 0x0084927aU},
    {0x00400c88U, 0x00400c88U, 0x008495e7U},
    {0x00400c8cU, 0x00400c8cU, 0x00849954U},
    {0x00400c90U, 0x00400c90U, 0x00849cc1U},
    {0x00400c94U, 0x00400c94U, 0x0084a02eU},
    {0x00400c98U, 0x00400c98U, 0x0084a39bU},
    {0x00400c9cU, 0x00400c9cU, 0x0084a708U},
    {0x00400ca0U, 0x00400ca0U, 0x0084aa75U},
    {0x00400ca4U, 0x00400ca4U, 0x0084ade2U},
    {0x00400ca8U, 0x00400ca8U, 0x0084b14fU},
    {0x00400cacU, 0x00400cacU, 0x0084b4bcU},
    {0x00400cb0U, 0x00400cb0U, 0x0084b829U},
    {0x00400cb4U, 0x00400cb4U, 0x0084bb96U},
    {0x00400cb8U, 0x00400cb8U, 0x0084bf03U},
    {0x00400cbcU, 0x00400cbcU, 0x0084c270U},
    {0x00400cc0U, 0x00400cc0U, 0x0084c5ddU},
    {0x00400cc4U, 0x00400cc4U, 0x0084c94aU}
};

void fifo_dispatch_packet_build(u32 g14, u32 site, u32 mem802008,
                                u32 *words)
{
    words[0] = 5U;
    words[1] = 18U;
    words[2] = 0x40e00000U;
    words[3] = 0x41800000U;
    words[4] = g14;
    words[5] = 21U;
    words[6] = site;
    words[7] = 19U;
    words[8] = 0x40400000U;
    words[9] = 0x40400000U;
    words[10] = 0x40400000U;
    words[11] = 58U;
    words[12] = mem802008;
    words[13] = 6U;
}

u32 fifo_dispatch_index(u32 g0)
{
    return g0 % 30U;
}

const u32 *fifo_dispatch_lookup(u32 idx)
{
    if (idx >= DISPATCH_TABLE_COUNT)
        return 0;
    return dispatch_table[idx];
}

typedef struct {
    u32 do_write;
    u32 w800010, w804000, w804004, w804008, w80400c;
} dispatch_regs_out;

void fifo_dispatch_regs(u32 ptr_deref, u32 e1, u32 e2,
                        dispatch_regs_out *o)
{
    if (ptr_deref == 0U) {
        o->do_write = 0U;
        return;
    }
    o->do_write = 1U;
    o->w800010 = 0x101U;
    o->w804000 = ptr_deref;
    o->w804004 = e1;
    o->w804008 = e2;
    o->w80400c = 0U;
}
