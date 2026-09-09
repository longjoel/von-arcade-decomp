/* Coin/credit settings renderer contract recovered from i960 0xf2170-f22e0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 title_x, title_y, title_string, title_renderer;
    recovered_u32 coin_start_address, coin_start_value, coin_start_string;
    recovered_u32 credit_start_address, credit_start_value, credit_start_string;
    recovered_u32 manual_setting_address, manual_setting_value, manual_setting_string;
    recovered_u32 manual_setting_special, status_renderer, label_wrapper;
    recovered_u32 return_target;
} recovered_diagnostic_coin_settings_render_result_f2170;

int
recovered_diagnostic_coin_settings_render_f2170(
    recovered_u32 coin_start, recovered_u32 credit_start,
    recovered_u32 manual_setting,
    recovered_diagnostic_coin_settings_render_result_f2170 *result)
{
    recovered_diagnostic_coin_settings_render_result_f2170 local = {0};
    local.title_x=18U; local.title_y=6U; local.title_string=0x000eafd0U;
    local.title_renderer=0x000eaf20U; local.coin_start_address=0x01d0002cU;
    local.coin_start_value=coin_start; local.credit_start_address=0x01d0002eU;
    local.credit_start_value=credit_start; local.manual_setting_address=0x01d0002aU;
    local.manual_setting_value=manual_setting; local.label_wrapper=0x000eaeb0U;
    local.status_renderer=0x000f1f20U; local.return_target=0x000f22e0U;
    local.coin_start_string=(coin_start==0U) ? 0x000f20f0U : 0x000f2100U;
    local.credit_start_string=(credit_start==0U) ? 0x000f20f0U : 0x000f2100U;
    local.manual_setting_special=(manual_setting==0U);
    local.manual_setting_string=(manual_setting==0U) ? 0x000f2150U : 0x000f2160U;
    if (result != (void *)0) *result=local;
    return 1;
}
