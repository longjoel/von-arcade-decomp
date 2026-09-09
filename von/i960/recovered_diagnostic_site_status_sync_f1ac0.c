/* Site/status synchronizer recovered from i960 0xf1ac0-f1bb8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 input_gate_result, early_return;
    recovered_u32 first_source, first_compare_word, first_compare_mask;
    recovered_u32 second_source, second_compare_word, second_compare_mask;
    recovered_u32 first_validation_call, second_validation_call;
    recovered_u32 first_validation_result, second_validation_result;
    recovered_u32 first_status_source, second_status_source, published_status;
    recovered_u32 published_status_address, service_state_address, service_state_value;
    recovered_u32 scratch_call, scratch_length, scratch_table;
    recovered_u32 failure_status, return_target;
} recovered_diagnostic_site_status_sync_result_f1ac0;

int
recovered_diagnostic_site_status_sync_f1ac0(
    recovered_u32 input_gate_result, recovered_u32 first_validation_result,
    recovered_u32 second_validation_result, recovered_u32 first_status,
    recovered_u32 second_status,
    recovered_diagnostic_site_status_sync_result_f1ac0 *result)
{
    recovered_diagnostic_site_status_sync_result_f1ac0 local = {0};
    local.input_gate_result=input_gate_result; local.first_source=0x00502408U;
    local.first_compare_word=0x00502408U; local.first_compare_mask=0xffffU;
    local.second_source=0x00502448U; local.second_compare_word=0x00502448U;
    local.second_compare_mask=0xffffU; local.first_validation_call=0x0000f5c58U;
    local.second_validation_call=0x0000f5c58U;
    local.first_validation_result=first_validation_result;
    local.second_validation_result=second_validation_result;
    local.first_status_source=0x00502422U; local.second_status_source=0x00502462U;
    local.published_status_address=0x01d00028U; local.service_state_address=0x005785b4U;
    local.service_state_value=1U; local.scratch_call=0x0000f5d40U;
    local.scratch_length=20U; local.scratch_table=0x0000f1ab0U;
    local.failure_status=2U; local.return_target=0x000f1bb8U;
    if (input_gate_result == 0U) {
        local.early_return=1U;
    } else if (first_validation_result == 0U) {
        local.published_status=first_status;
    } else if (second_validation_result == 0U) {
        local.published_status=second_status;
    } else {
        local.published_status=local.failure_status;
    }
    if (result != (void *)0) *result=local;
    return 1;
}
