/* Bookkeeping manual-setting arm recovered from i960 0xf2b60-f2bbc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 settings_renderer, pattern_address, pattern_value, clear_address;
    recovered_u32 probe_call, probe_result, setting_address, setting_before, setting_after;
    recovered_u32 modulus, zero_replacement, configuration_decoder;
    recovered_u32 bookkeeping_mode_address, bookkeeping_mode_value;
    recovered_u32 service_state_address, service_state_value, return_target;
} recovered_diagnostic_bookkeeping_manual_setting_arm_result_f2b60;

int
recovered_diagnostic_bookkeeping_manual_setting_arm_f2b60(
    recovered_u32 probe_result, recovered_u32 manual_setting,
    recovered_diagnostic_bookkeeping_manual_setting_arm_result_f2b60 *result)
{
    recovered_diagnostic_bookkeeping_manual_setting_arm_result_f2b60 local = {0};
    local.settings_renderer=0x000f2170U; local.pattern_address=0x01004822U;
    local.pattern_value=30U; local.clear_address=0x01004722U;
    local.probe_call=0x000eade8U; local.probe_result=probe_result;
    local.setting_address=0x01d0002aU; local.setting_before=manual_setting; local.modulus=28U;
    local.setting_after=(probe_result!=0U) ? ((manual_setting+1U)%28U) : manual_setting;
    local.zero_replacement=1U; if (local.setting_after==0U) local.setting_after=1U;
    local.configuration_decoder=0x000f19e8U; local.bookkeeping_mode_address=0x00578524U;
    local.bookkeeping_mode_value=1U; local.service_state_address=0x005785b4U;
    local.service_state_value=1U; local.return_target=0x000f2bbcU;
    if (result != (void *)0) *result=local;
    return 1;
}
