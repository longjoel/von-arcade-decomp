/* Coin-chute status renderer contract recovered from i960 0xf1f20-f20a4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_address, status_word;
    recovered_u32 input_x, input_y, first_x, first_y, second_x, second_y;
    recovered_u32 early_return, type27_special;
    recovered_u32 first_table_index, second_table_index, table_address;
    recovered_u32 first_value_a, first_value_b, first_value_c;
    recovered_u32 second_value_a, second_value_b, second_value_c;
    recovered_u32 first_formatter, second_formatter, label_wrapper;
    recovered_u32 type_string, free_play_string, blank_string, return_target;
} recovered_diagnostic_coin_chute_status_render_result_f1f20;

int
recovered_diagnostic_coin_chute_status_render_f1f20(
    recovered_u32 status_word, recovered_u32 x, recovered_u32 y,
    recovered_diagnostic_coin_chute_status_render_result_f1f20 *result)
{
    recovered_diagnostic_coin_chute_status_render_result_f1f20 local = {0};
    local.status_address=0x01d0002aU; local.status_word=status_word;
    local.input_x=x; local.input_y=y; local.first_x=x-18U;
    local.first_y=y; local.second_x=x-18U; local.second_y=y+6U;
    local.table_address=0x000ead30U; local.label_wrapper=0x000eaeb0U;
    local.type_string=0x000f1ec0U; local.free_play_string=0x000f1ee0U;
    local.blank_string=0x000f1d90U; local.return_target=0x000f20a4U;
    if ((status_word & 0xffffU) == 0U) { local.early_return=1U; if (result != (void *)0) *result=local; return 1; }
    local.type27_special=((status_word & 0xffffU) == 27U);
    local.first_table_index=(status_word & 0xffffU) << 2U;
    local.second_table_index=local.first_table_index;
    if (!local.type27_special) {
        /* ead30 lookups use offsets 0,2,3 for the first formatter call. */
        local.first_value_a=0xead30U+local.first_table_index;
        local.first_value_b=0xead32U+local.first_table_index;
        local.first_value_c=0xead33U+local.first_table_index;
        /* The second call reuses the packed index with offsets 0,1,3. */
        local.second_value_a=0xead30U+local.second_table_index;
        local.second_value_b=0xead31U+local.second_table_index;
        local.second_value_c=0xead33U+local.second_table_index;
        local.first_formatter=0x000f1db0U; local.second_formatter=0x000f1db0U;
    }
    if (result != (void *)0) *result=local;
    return 1;
}
