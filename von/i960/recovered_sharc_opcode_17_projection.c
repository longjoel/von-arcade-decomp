/* Composed normal-path model for SHARC opcode 0x17 and helper 0x20de1. */
#include <stddef.h>
#include <stdint.h>

typedef uint32_t u32;

extern int recovered_sharc_opcode_17_select_record(
    const u32 *selectors, u32 selector_count, u32 ordinal,
    const u32 *record_bank, size_t record_words, float r8, float r9,
    u32 staged[12], float *determinant);
extern int recovered_sharc_helper_20de1_plane_y(
    const u32 record[12], float x, float z, u32 *result);
extern int recovered_sharc_helper_20de1_plane_y_recips(
    const u32 record[12], float x, float z, u32 *result);

/*
 * Return values preserve the caller's gate distinction:
 *   -1 invalid selector/bank, 0 zero determinant, 1 normal result,
 *   -2 helper rejected the selected record as geometrically degenerate.
 */
int recovered_sharc_opcode_17_project_record(
    const u32 *selectors, u32 selector_count, u32 ordinal,
    const u32 *record_bank, size_t record_words, float r8, float r9,
    u32 staged[12], float *determinant, u32 *result)
{
    int const selected = recovered_sharc_opcode_17_select_record(
        selectors, selector_count, ordinal, record_bank, record_words,
        r8, r9, staged, determinant);
    if (selected != 1)
        return selected;
    if (!recovered_sharc_helper_20de1_plane_y_recips(staged, r8, r9, result))
        return -2;
    return 1;
}
