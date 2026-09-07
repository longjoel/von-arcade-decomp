/* Post-call setup tail, i960 routine range 0x00076030-0x000761a8
 * (continuation of the 0x75d90 stage setup; the nested call at
 * 0x76030 to 0x86240 is another agent's slice and forms the lower
 * boundary: post-call g14/r4 arrive from the callee).
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst:
 *   76034  [0x504e1c] = 1
 *   76040  stos g14 -> [0x504e42]            16-bit
 *   76048  [0x504e44] = g14
 *   76050  [0x504e20] = r4
 *   76058  g5 = [0x5770f0]                   50-byte row index
 *   76060  [0x504e24] = r4
 *   76068  [0x504e28] = g14
 *   76070  [0x504e2c] = g14
 *   76078  g4 = 25 * g5 (shlo/addo chain)
 *   76088  g4 = 0x72400 + 50 * g5            50-byte rows
 *   76090  quad[0x505060] = quad[g4]         16 bytes @ +0x00
 *   7609c  quad[0x505070] = quad[g4+0x10]    16 bytes @ +0x10
 *   760a8  quad[0x505080] = quad[g4+0x20]    16 bytes @ +0x20
 *   760b4  ldos [g4+0x30] -> stos [0x505090] 2 bytes @ +0x30
 *   760c0  first 0x72370 read keyed by the r5 chain
 *          (g4 = [0x74(r5)], g5 = [0x64(g4)] & 7); g0 = 0x72370
 *   760ec  ldl [entry] (8 bytes) -> stl [0x504e34] (covers e34+e38)
 *   760f0  [0x509b8c/90] = g14
 *   760f8  [0x504e3c] = word[entry+8]
 *   76100+ [0x504e3c] = word[entry+8]
 *   76114  ldos [entry+0xc] -> provisional stos [0x504e40]
 *   76118  [0x509b94/98] = g14
 *   76128  cmpi [0x5039f4],4; be 0x7618c takes the first read live
 *   76138  second 0x72370 read iff [0x5039f4] != 4, keyed by
 *          (([0x68(r5)] == 0) ? [0x503a9c] : [0x503a98]) & 7,
 *          overwriting e34/e38/e3c/e40
 *   7618c  stob g14 -> [0x504e50]            8-bit
 *   76198  [0x504e4c] = g14
 *   761a0  [0x504e48] = 6
 *   761a8  ret
 * (ldl/stl move 8 bytes as a g6/g7 pair; compare flags are src1 -
 * src2 per the 0x75d90 operand-order anchors.)
 *
 * Live goldens (spawn dumps d1-d4; post-call g14 = 0, r4 = -1):
 * e1c = 1; e42/e44/e28/e2c/9b8c/90/94/98 = 0; e20/e24 = -1;
 * e48 = 6; e4c/e50 = 0.
 * 0x72400 rows (50 bytes = 12 words + half, read live from ROM):
 * S3 (both attempts) = row 2, S4 = row 3, so [0x5770f0] tracks
 * the stage ordinal here (2/3).
 * 0x72370 entries (14 bytes = 4 halves + word + half, ROM):
 * S3 attempt 1 = entry 4, S3 attempt 3 = entry 6, S4 = entry 3;
 * continues re-pick the entry while reusing the 0x72400 row.
 * Entry keys (r5 chain) stay unresolved inputs.
 */

typedef unsigned int u32;

#define ROW724_BASE 0x72400U
#define ROW724_STRIDE 50U
#define ROW724_WORDS 12U
#define ROW724_COUNT 8U

static const u32 row724_table[ROW724_COUNT][ROW724_WORDS] = {
    {0x00c8ff74U, 0xff240028U, 0x00280000U, 0xff38ff74U, 0x008c0028U,
     0x002800c8U, 0x000000dcU, 0x008c0028U, 0x0028ff38U, 0x003c0000U,
     0x00000028U, 0x0028ffc4U},
    {0x0064ff4cU, 0xff4c001eU, 0x001eff9cU, 0x00dc0014U, 0x0000001eU,
     0x003c0000U, 0xff24ffecU, 0x00b4001eU, 0x001e0064U, 0xff9c00b4U,
     0x0000001eU, 0x00000000U},
    {0x0064ff24U, 0xfefc001eU, 0x001e003cU, 0x003cff24U, 0xffb0001eU,
     0x003c00f0U, 0x00000000U, 0x00f00000U, 0x003c0050U, 0x00000000U,
     0x00000000U, 0x00000000U},
    {0x00000000U, 0x00000000U, 0x00000000U, 0x00000000U, 0x00000000U,
     0x00000000U, 0x00000000U, 0x00000000U, 0x00000000U, 0x00000000U,
     0x00000000U, 0x00000000U},
    {0x008cff74U, 0xff74001eU, 0x001eff74U, 0x008c008cU, 0x008c001eU,
     0x001eff74U, 0x00000000U, 0x00000000U, 0x00000000U, 0x00000000U,
     0x00000000U, 0x00000000U},
    {0x0078ff88U, 0xff88003cU, 0x003c0028U, 0xff88ff88U, 0xff88003cU,
     0x003cff38U, 0x002800a0U, 0x00a0003cU, 0x003cffd8U, 0xff8800a0U,
     0x0000003cU, 0x00000000U},
    {0x00b4ff9cU, 0xff24001eU, 0x00320050U, 0xff9cff24U, 0xffb0001eU,
     0x0032ff4cU, 0x00b40064U, 0x00dc001eU, 0x00320050U, 0xff9c00dcU,
     0x0050001eU, 0x0032ff4cU},
    {0x00b4ff4cU, 0xff9c001eU, 0x003c0000U, 0xff4cff4cU, 0x00b4001eU,
     0x001e00b4U, 0x00000064U, 0x00b4003cU, 0x001eff4cU, 0x00000000U,
     0x00000000U, 0x00000000U}
};

static const u32 row724_half[ROW724_COUNT] = {
    0x0190U, 0x0190U, 0x0190U, 0x0226U,
    0x0186U, 0x01aeU, 0x0190U, 0x0190U
};

#define ROW370_BASE 0x72370U
#define ROW370_STRIDE 14U
#define ROW370_COUNT 8U

static const unsigned short row370_table[ROW370_COUNT][7] = {
    {0x000dU, 0x0000U, 0x0001U, 0x0007U, 0x0032U, 0x003cU, 0x0032U},
    {0x131fU, 0x0000U, 0x0000U, 0x0019U, 0x003cU, 0x003cU, 0x003cU},
    {0x3731U, 0x0000U, 0x0025U, 0x002bU, 0x0050U, 0x0050U, 0x003cU},
    {0x0049U, 0x0000U, 0x003dU, 0x0043U, 0x005aU, 0x0064U, 0x003cU},
    {0x004fU, 0x0000U, 0x615bU, 0x0055U, 0x003cU, 0x003cU, 0x003cU},
    {0x6d67U, 0x857fU, 0x0000U, 0x7973U, 0x0064U, 0x0064U, 0x0064U},
    {0x0097U, 0x0000U, 0x008bU, 0x0091U, 0x003cU, 0x003cU, 0x003cU},
    {0xa99dU, 0x00afU, 0x0000U, 0x00a3U, 0x003cU, 0x003cU, 0x003cU}
};

u32 row724_address(u32 idx)
{
    return ROW724_BASE + idx * ROW724_STRIDE;
}

const u32 *row724_lookup(u32 idx)
{
    if (idx >= ROW724_COUNT)
        return 0;
    return row724_table[idx];
}

u32 row724_tail_half(u32 idx)
{
    if (idx >= ROW724_COUNT)
        return 0;
    return row724_half[idx];
}

void row724_copy(const u32 *src_row, u32 src_half, u32 *dst_words,
                 u32 *dst_half)
{
    u32 i;
    for (i = 0; i < ROW724_WORDS; i++)
        dst_words[i] = src_row[i];
    *dst_half = src_half & 0xffffU;
}

typedef struct {
    u32 e34, e38, e3c;
    u32 e40;
} entry370_out;

void read370(unsigned key, entry370_out *o)
{
    const unsigned short *e = row370_table[key & 7U];
    o->e34 = (u32)e[0] | ((u32)e[1] << 16);
    o->e38 = (u32)e[2] | ((u32)e[3] << 16);
    o->e3c = (u32)e[4] | ((u32)e[5] << 16);
    o->e40 = (u32)e[6];
}

u32 second370_key(u32 r5f68, u32 a98, u32 a9c)
{
    return (((r5f68 == 0U) ? a9c : a98) & 7U);
}

typedef struct {
    u32 e1c, e42, e44, e20, e24, e28, e2c, e50, e4c, e48;
    u32 b8c, b90, b94, b98;
} postcall_const_out;

void postcall_consts(u32 g14, u32 r4, postcall_const_out *o)
{
    o->e1c = 1U;
    o->e42 = g14 & 0xffffU;
    o->e44 = g14;
    o->e20 = r4;
    o->e24 = r4;
    o->e28 = g14;
    o->e2c = g14;
    o->e50 = g14 & 0xffU;
    o->e4c = g14;
    o->e48 = 6U;
    o->b8c = g14;
    o->b90 = g14;
    o->b94 = g14;
    o->b98 = g14;
}
