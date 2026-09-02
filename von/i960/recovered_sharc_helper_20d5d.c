/* Semantic model of SHARC helper 0x20d5d's external table-base derivation. */

typedef unsigned int u32;

void recovered_sharc_helper_20d5d_derive(u32 base, u32 table_at_10,
                                         u32 table_at_20, u32 output[2])
{
    (void)base;
    output[0] = table_at_10 + 0x01c00000U;
    output[1] = table_at_20 + 0x01c00000U;
}
