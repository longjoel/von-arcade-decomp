/* Recovered selector/staging and determinant gate for SHARC opcode 0x17. */
#include <stddef.h>
#include <stdint.h>
#include "recovered_float.h"

typedef uint32_t u32;

/*
 * Select one entry from the streamed table and stage its twelve-word record.
 * The ROM shifts the selected table value left by four before applying it to
 * the 16-word-stride record bank.  The return value is 1 for a nonzero signed
 * determinant, 0 for the ROM's equal/zero gate, and -1 for an invalid bank
 * window.  The helper 0x20de1 is intentionally outside this contract.
 */
int recovered_sharc_opcode_17_select_record(const u32 *selectors,
                                             u32 selector_count,
                                             u32 ordinal,
                                             const u32 *record_bank,
                                             size_t record_words,
                                             float r8, float r9,
                                             u32 staged[12],
                                             float *determinant)
{
    if (ordinal >= selector_count)
        return -1;

    size_t offset = (size_t)selectors[ordinal] * 16U;
    if (offset > record_words || record_words - offset < 12U)
        return -1;

    for (size_t index = 0; index < 12U; ++index)
        staged[index] = record_bank[offset + index];

    float value = (r8 - recovered_float_from_bits(staged[3])) *
                  (recovered_float_from_bits(staged[2]) - recovered_float_from_bits(staged[5])) -
                  (r9 - recovered_float_from_bits(staged[5])) *
                  (recovered_float_from_bits(staged[0]) - recovered_float_from_bits(staged[3]));
    if (determinant != NULL)
        *determinant = value;
    return value == 0.0f ? 0 : 1;
}
