/* SHARC opcode-0x07 affine-state store, FIFO behavioral contract.
 *
 * Opcode 0x07 loads the 12-word affine state (row-major 3x3 at slots
 * 0..8, translation at 9..11) consumed by opcode 0x1a's
 * column-accumulating transform. Live hardware probing
 * (von/build/probe_sharc_opcode_07_store.lua) shows the store is
 * verbatim: across identity, scaled, non-symmetric, and fractional
 * trials, feeding the stored state to the trusted 0x1a model
 * reproduces the observed response words exactly, excluding
 * transpose, negation, scaling, and fixed-point conversion.
 * The SHARC-side handler PC is unmapped (dispatch table open), so
 * this contract covers the FIFO behavior only.
 */

typedef unsigned int u32;

#define AFFINE_STATE_WORDS 12U

void recovered_sharc_opcode_07_store(const u32 incoming[AFFINE_STATE_WORDS],
                                     u32 state[AFFINE_STATE_WORDS])
{
    unsigned i;
    for (i = 0; i < AFFINE_STATE_WORDS; i++)
        state[i] = incoming[i];
}
