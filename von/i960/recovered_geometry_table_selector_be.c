/* Shared selector logic recovered from i960 0xbedf0, 0xbeee0, and 0xbefd0. */
#include "recovered_common.h"

typedef enum {
    RECOVERED_GEOMETRY_TABLE_FAMILY_BCC = 0,
    RECOVERED_GEOMETRY_TABLE_FAMILY_BCD = 1,
    RECOVERED_GEOMETRY_TABLE_FAMILY_BCE = 2
} recovered_geometry_table_family_be;

typedef struct {
    recovered_u32 table_address;
    recovered_u32 selector_offset;
    recovered_u32 normalized_172;
    recovered_u32 normalized_188;
} recovered_geometry_table_selection_be;

/*
 * The three ROM routines have the same decision tree.  Their cmpibl arm is
 * the range above 24 (the immediate is the first compare operand), with 31
 * then refined by the low signed halfword at +0x188.  The final table record
 * is selected by the unsigned +0x64 field times 24 bytes.
 */
int recovered_geometry_table_select_be(
    recovered_geometry_table_family_be family,
    recovered_u32 field_64,
    recovered_u32 field_172,
    recovered_u32 field_188,
    recovered_geometry_table_selection_be *selection)
{
    static const recovered_u32 bases[3] = {
        0x000bcc70U, 0x000bcd60U, 0x000bce50U
    };
    recovered_u32 first = (recovered_u32)(int)(int16_t)(field_172 & 0xffffU);
    recovered_u32 second = (recovered_u32)(int)(int16_t)(field_188 & 0xffffU);
    recovered_u32 offset;

    if ((unsigned)family >= 3U || selection == (void *)0)
        return 0;

    if (first == 24U) {
        offset = 0x10U;
    } else if (first > 24U && first == 31U) {
        if (second == 0U)
            offset = 0x04U;
        else if (second == 1U)
            offset = 0x0cU;
        else
            offset = 0x08U;
    } else if (first == 14U) {
        offset = 0x14U;
    } else {
        offset = 0U;
    }

    selection->selector_offset = offset;
    selection->normalized_172 = first;
    selection->normalized_188 = second;
    selection->table_address = bases[family] + offset + field_64 * 24U;
    return 1;
}
