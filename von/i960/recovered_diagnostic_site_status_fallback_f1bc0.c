/* Site/status fallback arm recovered from i960 0xf1bc0-f1bdc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 input_gate_result, early_return;
    recovered_u32 mode_address, mode_value;
    recovered_u32 result_state_address, result_state_value;
    recovered_u32 probe_call, return_target;
} recovered_diagnostic_site_status_fallback_result_f1bc0;

int
recovered_diagnostic_site_status_fallback_f1bc0(
    recovered_u32 input_gate_result,
    recovered_diagnostic_site_status_fallback_result_f1bc0 *result)
{
    recovered_diagnostic_site_status_fallback_result_f1bc0 local = {0};
    local.input_gate_result=input_gate_result; local.mode_address=0x005784f8U;
    local.mode_value=2U; local.result_state_address=0x00578500U;
    local.result_state_value=0U; local.probe_call=0x000eade8U;
    local.return_target=0x000f1bdcU;
    if (input_gate_result == 0U) local.early_return=1U;
    if (result != (void *)0) *result=local;
    return 1;
}
