/* Bookkeeping diagnostic service contract recovered from i960 0xf2e20-f2ee4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 result_state_before, result_state_after, initialized;
    recovered_u32 branch_address, branch_value, probe_result;
    recovered_u32 counter_address, counter_before, counter_after, counter_modulus;
    recovered_u32 table_address, selected_index, selected_handler;
    recovered_u32 alternate_counter_address, alternate_counter_before, alternate_counter_after;
    recovered_u32 alternate_table_address, alternate_index, alternate_handler;
    recovered_u32 initialization_call, probe_call, handler_call, return_target;
} recovered_diagnostic_bookkeeping_service_result_f2e20;

int
recovered_diagnostic_bookkeeping_service_f2e20(
    recovered_u32 result_state, recovered_u32 branch_value,
    recovered_u32 primary_probe, recovered_u32 alternate_probe,
    recovered_u32 primary_counter, recovered_u32 alternate_counter,
    const recovered_u32 primary_table[5], const recovered_u32 alternate_table[5],
    recovered_diagnostic_bookkeeping_service_result_f2e20 *result)
{
    recovered_diagnostic_bookkeeping_service_result_f2e20 local = {0};
    local.result_state_before=result_state; local.result_state_after=result_state;
    local.initialized=(result_state==0U); if (local.initialized) local.result_state_after=0xffffffffU;
    local.branch_address=0x00578524U; local.branch_value=branch_value;
    local.counter_address=0x0057851cU; local.counter_before=primary_counter;
    local.alternate_counter_address=0x00578520U; local.alternate_counter_before=alternate_counter;
    local.counter_modulus=5U; local.initialization_call=0x0001c618U;
    local.probe_call=0x000eada8U; local.table_address=0x000f2de0U;
    local.alternate_table_address=0x000f2e00U; local.return_target=0x000f2ee4U;
    if (branch_value==0U) {
        local.probe_result=primary_probe;
        local.counter_after=(primary_probe!=0U) ? ((primary_counter+1U)%5U) : primary_counter;
        local.selected_index=local.counter_after&7U;
        local.selected_handler=(primary_table != (void *)0 && local.selected_index<5U) ? primary_table[local.selected_index] : 0U;
        local.handler_call=local.selected_handler;
    } else {
        local.probe_result=alternate_probe;
        local.alternate_counter_after=(alternate_probe!=0U) ? ((alternate_counter+1U)%5U) : alternate_counter;
        local.alternate_index=local.alternate_counter_after&7U;
        local.alternate_handler=(alternate_table != (void *)0 && local.alternate_index<5U) ? alternate_table[local.alternate_index] : 0U;
        if (local.alternate_handler==0U) local.alternate_counter_after+=1U;
        local.handler_call=local.alternate_handler;
    }
    if (result != (void *)0) *result=local;
    return 1;
}
