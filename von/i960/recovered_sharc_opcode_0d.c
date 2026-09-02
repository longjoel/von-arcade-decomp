/* Model of the SHARC opcode-0x0d/helper-0x20d5d pointer initializer. */

typedef unsigned int u32;

/* The helper reads the two external table words relative to base.  The
 * fetched values are supplied by the caller so the address contract remains
 * explicit without embedding a particular ROM/RAM image. */
void recovered_sharc_opcode_0d_publish(u32 base, u32 table_word_10,
                                       u32 table_word_20, u32 output[2])
{
    (void)base;
    output[0] = table_word_10 + 0x01c00000U;
    output[1] = table_word_20 + 0x01c00000U;
}
