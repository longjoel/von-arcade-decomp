/* Coin/credit diagnostic service contract recovered from i960 0xf1c90-f1d40. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 result_state_address, result_state_before, result_state_after;
    recovered_u32 initialization_call, initialization_performed;
    recovered_u32 dispatch_result, index_address, index_before, index_after;
    recovered_u32 index_modulus, table_address, table_entry_count;
    recovered_u32 table_handler[20], table_selector[20];
    recovered_u32 pattern_base, pattern_stride, pattern_index, pattern_destination, pattern_value;
    recovered_u32 formatter_call, selected_handler_call, return_target;
} recovered_diagnostic_coin_credit_service_result_f1c90;

int
recovered_diagnostic_coin_credit_service_f1c90(
    recovered_u32 result_state, recovered_u32 dispatch_result,
    recovered_u32 index, recovered_diagnostic_coin_credit_service_result_f1c90 *result)
{
    static const recovered_u32 handlers[20] = {
        0x000f1bc0U,0x000f14a0U,0x000f1520U,0x000f15a0U,0x000f1620U,
        0x000f16a0U,0x000f1720U,0x000f1750U,0x000f1780U,0x000f17b0U,
        0x000f17e0U,0x000f1810U,0x000f1840U,0x000f1890U,0x000f18c0U,
        0x000f1970U,0x000f19a0U,0x000f1930U,0x000f1900U,0x000f1ac0U};
    static const recovered_u32 selectors[20] = {
        0U,1U,2U,3U,4U,6U,7U,8U,9U,11U,13U,15U,17U,19U,21U,23U,25U,27U,29U,31U};
    recovered_diagnostic_coin_credit_service_result_f1c90 local = {0};
    local.result_state_address = 0x00578500U; local.result_state_before = result_state;
    local.result_state_after = result_state; local.initialization_call = 0x0001c618U;
    local.initialization_performed = (result_state == 0U);
    if (local.initialization_performed) local.result_state_after = 0xffffffffU;
    local.dispatch_result = dispatch_result; local.index_address = 0x00578518U;
    local.index_before = index; local.index_modulus = 20U;
    local.index_after = (dispatch_result == 0U) ? index : ((index + 1U) % 20U);
    local.table_address = 0x000f1be0U; local.table_entry_count = 20U;
    for (recovered_u32 i = 0U; i < 20U; ++i) { local.table_handler[i] = handlers[i]; local.table_selector[i] = selectors[i]; }
    local.pattern_base = 0x0100451cU; local.pattern_stride = 0x80U;
    local.pattern_index = 0x1fU;
    local.pattern_destination = local.pattern_base + local.pattern_index * local.pattern_stride;
    local.pattern_value = 30U; local.formatter_call = 0x000f0f10U;
    local.selected_handler_call = (dispatch_result == 0U) ? 0U : handlers[local.index_after];
    local.return_target = 0x000f1d40U;
    if (result != (recovered_diagnostic_coin_credit_service_result_f1c90 *)0) *result = local;
    return 1;
}
