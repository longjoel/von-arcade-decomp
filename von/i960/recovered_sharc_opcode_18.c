/* Exact table-window transfer recovered from SHARC opcode 0x18. */
typedef unsigned int u32;

/*
 * The FIFO operand is a record index. SHARC shifts it left four bits before
 * MODIFY(I7, M7), selecting one 16-word record. The service copies that
 * record into the 16-word scratch window, then streams its first 12 words.
 */
void recovered_sharc_opcode_18_window(const u32 *table,
                                       u32 record_index,
                                       u32 scratch[16],
                                       u32 output[12])
{
    u32 source = record_index * 16U;
    u32 index;

    for (index = 0; index < 16U; ++index)
        scratch[index] = table[source + index];
    for (index = 0; index < 12U; ++index)
        output[index] = scratch[index];
}
