/* Bookkeeping credit-start arm recovered from i960 0xf2ae0-f2b58. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 settings_renderer, pattern_address, pattern_value, clear_address;
    recovered_u32 probe_call, probe_result, credit_address, credit_before, credit_after;
    recovered_u32 coin_address, coin_before, coin_after, modulus;
    recovered_u32 service_state_address, service_state_value, return_target;
} recovered_diagnostic_bookkeeping_credit_start_arm_result_f2ae0;

int
recovered_diagnostic_bookkeeping_credit_start_arm_f2ae0(
    recovered_u32 probe_result, recovered_u32 credit_start,
    recovered_u32 coin_start,
    recovered_diagnostic_bookkeeping_credit_start_arm_result_f2ae0 *result)
{
    recovered_diagnostic_bookkeeping_credit_start_arm_result_f2ae0 local = {0};
    local.settings_renderer=0x000f2170U; local.pattern_address=0x01004722U;
    local.pattern_value=30U; local.clear_address=0x01004622U;
    local.probe_call=0x000eade8U; local.probe_result=probe_result;
    local.credit_address=0x01d0002eU; local.credit_before=credit_start; local.modulus=5U;
    local.credit_after=(probe_result!=0U) ? ((credit_start+1U)%5U) : credit_start;
    local.coin_address=0x01d0002cU; local.coin_before=coin_start;
    local.coin_after=coin_start;
    if (local.credit_after>coin_start) local.credit_after=0U;
    local.service_state_address=0x005785b4U; local.service_state_value=1U;
    local.return_target=0x000f2b58U;
    if (result != (void *)0) *result=local;
    return 1;
}
