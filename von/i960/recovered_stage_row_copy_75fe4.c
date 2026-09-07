/* Stage-row table copy, i960 routine tail at 0x00075fe4.
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst:
 *   75fe4  g4 = word[0x64(g0)]            row index from bout struct
 *   75fe8  g4 = g4 + g4 * 8               9 * idx
 *   75fec  g4 = 0x72050 + g4 * 8          0x72050 + 72 * idx
 *   75ff4  quad[0x504dd4] = quad[g4]      16 bytes @ +0x00
 *   76000  quad[0x504de4] = quad[g4+0x10] 16 bytes @ +0x10
 *   7600c  quad[0x504df4] = quad[g4+0x20] 16 bytes @ +0x20
 *   76018  quad[0x504e04] = quad[g4+0x30] 16 bytes @ +0x30
 *   76024  long[0x504e14] = long[g4+0x40] 8 bytes @ +0x40
 * (ldq moves 16 bytes, ldl 8: 72 bytes total. The nested call at
 * 0x76030 and everything after it is a separate slice.)
 *
 * Table content read live from ROM through the maincpu program space
 * (von/build/probe_rom_rows.lua, no playback needed). Row identities
 * verified against spawn RAM dumps (whole 18-word rows match exactly):
 * faithful S3 (attempts 1 and 3, same row) = row 4, faithful S4 =
 * row 2, warped S4-in-slot-1 = row 0. Continues reuse the row, so the
 * S3 0x504dbc 0x20/0x1c split lives outside this copy.
 *
 * The index-to-stage mapping itself (word[0x64(g0)]) is unresolved:
 * S3 -> 4, S4 -> 2, warp slot 1 -> 0. Word +0x0c varies per row
 * (3/2/3/3/2/3/3/3) and is not the plain stage ordinal (no row
 * carries 0 or 1), so rows are not simply per-stage slots.
 */

typedef unsigned int u32;

#define STAGE_ROW_BASE 0x72050U
#define STAGE_ROW_STRIDE 72U
#define STAGE_ROW_WORDS 18U
#define STAGE_ROW_COUNT 8U

static const u32 stage_row_table[STAGE_ROW_COUNT][STAGE_ROW_WORDS] = {
    {0x00c80032U, 0x0000012cU, 0x0000001eU, 0x00000003U, 0x00646580U,
     0x000a0046U, 0x00050014U, 0x00c80028U, 0x005a005aU, 0x00640019U,
     0x0000012cU, 0x0000001eU, 0x0046001eU, 0x00960046U, 0x00fa004bU,
     0x00000320U, 0x0000000aU, 0x00000000U},
    {0x00c80032U, 0x0000012cU, 0x0000001eU, 0x00000002U, 0x00646580U,
     0x000a0046U, 0x00050014U, 0x00c80028U, 0x00640064U, 0x0064000fU,
     0x0000012cU, 0x00000014U, 0x0046001eU, 0x00960046U, 0x012c00c8U,
     0x00000320U, 0x0000001eU, 0x00000000U},
    {0x00c80064U, 0x0000015eU, 0x0000001eU, 0x00000003U, 0x00646000U,
     0x000a0046U, 0x00050014U, 0x00c80028U, 0x00640064U, 0x0064000fU,
     0x0000012cU, 0x00000005U, 0x0046001eU, 0x00960046U, 0x006400faU,
     0x00000320U, 0x0000001eU, 0x00000000U},
    {0x00960032U, 0x0000012cU, 0x0000001eU, 0x00000003U, 0x00646000U,
     0x000a0046U, 0x00050014U, 0x00c80028U, 0x00640064U, 0x0064000fU,
     0x0000012cU, 0x00000005U, 0x0046001eU, 0x00960046U, 0x003200dcU,
     0x00000320U, 0x0000001eU, 0x00000000U},
    {0x00fa0032U, 0x0000012cU, 0x0000001eU, 0x00000002U, 0x00646000U,
     0x000a0046U, 0x00050014U, 0x00c80028U, 0x005f005fU, 0x0064000fU,
     0x0000012cU, 0x00000014U, 0x0046001eU, 0x00960046U, 0x00820190U,
     0x00000320U, 0x0000001eU, 0x00000000U},
    {0x00c80032U, 0x0000012cU, 0x0000001eU, 0x00000003U, 0x00646580U,
     0x000a0046U, 0x00050014U, 0x00c80028U, 0x005a005aU, 0x0064000fU,
     0x0000012cU, 0x00000005U, 0x0046001eU, 0x00960046U, 0x006400a0U,
     0x00000320U, 0x0000001eU, 0x00000000U},
    {0x0064000aU, 0x00000096U, 0x0000001eU, 0x00000003U, 0x00646580U,
     0x000a0046U, 0x00050014U, 0x00c80028U, 0x005a005aU, 0x006400a0U,
     0x0000012cU, 0x00000005U, 0x0046001eU, 0x00960046U, 0x00960096U,
     0x00000320U, 0x0000001eU, 0x00000000U},
    {0x00960032U, 0x0000012cU, 0x0000001eU, 0x00000003U, 0x00645000U,
     0x000a0046U, 0x00050014U, 0x00c80028U, 0x00640064U, 0x0064000fU,
     0x0000012cU, 0x00000005U, 0x0046001eU, 0x00960046U, 0x0032003cU,
     0x00000320U, 0x0000001eU, 0x00000000U}
};

u32 stage_row_address(u32 idx)
{
    return STAGE_ROW_BASE + idx * STAGE_ROW_STRIDE;
}

const u32 *stage_row_lookup(u32 idx)
{
    if (idx >= STAGE_ROW_COUNT)
        return 0;
    return stage_row_table[idx];
}

void stage_row_copy(const u32 *src_row, u32 *dst)
{
    u32 i;
    for (i = 0; i < STAGE_ROW_WORDS; i++)
        dst[i] = src_row[i];
}
