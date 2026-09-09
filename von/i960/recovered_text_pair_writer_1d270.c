/* Pure schedule for the two-row text pair writer at i960 0x1d270. */

#include <stdint.h>

typedef uint32_t u32;
typedef uint16_t u16;

/*
 * The caller supplies the words represented by the selected table window.
 * The ROM indexes two consecutive four-byte entries, writing one halfword
 * pair on each of two adjacent tile rows.
 */
u32 recovered_text_pair_writer_plan(
    u32 value,
    u32 row,
    u32 column,
    const u16 *table_words,
    u32 *selector,
    u32 *table_address,
    u32 *first_address,
    u32 *first_value,
    u32 *second_address,
    u32 *second_value,
    u32 *third_address,
    u32 *third_value,
    u32 *fourth_address,
    u32 *fourth_value,
    u32 *next_column)
{
    u32 normalized = value - 0x30U;
    u32 tile = (row << 6) + column;
    u32 address = 0x01000000U + (tile << 1);

    *selector = normalized & 0x0fU;
    *table_address = 0x02ea1dd0U + (*selector * 4U);
    *first_address = address;
    *first_value = ((u32)table_words[0] | 0x8000U) & 0xffffU;
    *second_address = address + 2U;
    *second_value = ((u32)table_words[1] | 0x8000U) & 0xffffU;
    *third_address = address + 0x80U;
    *third_value = ((u32)table_words[2] | 0x8000U) & 0xffffU;
    *fourth_address = address + 0x82U;
    *fourth_value = ((u32)table_words[3] | 0x8000U) & 0xffffU;
    *next_column = column <= 61U ? column + 2U : column;
    return 1U;
}
