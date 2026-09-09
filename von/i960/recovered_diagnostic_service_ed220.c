/* Diagnostic service state machine recovered from i960 0xed220-ed300. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 result_state_before, result_state_initialized;
    recovered_u32 reset_performed;
    recovered_u32 reset_call, initial_format_call, initial_format_x, initial_format_y;
    recovered_u32 prompt_string_address, prompt_renderer, menu_renderer;
    recovered_u32 event_mode_flag, dispatch_counter, dispatch_handler_address;
    recovered_u32 dispatch_handler_table, dispatch_save_address;
    recovered_u32 fallback_call, fallback_status_value, fallback_save_address;
    recovered_u32 status_counter_address, return_target;
} recovered_diagnostic_service_result_ed220;

recovered_diagnostic_service_result_ed220
recovered_diagnostic_service_ed220(
    recovered_u32 result_state, recovered_u32 event_mode_flag,
    recovered_u32 dispatch_counter, recovered_u32 fallback_result)
{
    static const recovered_u32 handlers[25] = {
        0xeca30U,0xeca60U,0xeca90U,0xecac0U,0xecaf0U,0xecb20U,
        0xeb2c0U,0xebab0U,0xec920U,0xebe20U,0xebc60U,0xebfd0U,
        0xec140U,0xec290U,0xec3e0U,0xec8f0U,0xec480U,0xec760U,
        0xec630U,0xeb830U,0xec8f0U,0xec940U,0xec940U,0xec940U,0xec940U
    };
    recovered_diagnostic_service_result_ed220 result;
    result.result_state_before=result_state; result.result_state_initialized=result_state == 0U ? 1U : 0U;
    result.reset_performed=result_state == 0U ? 1U : 0U;
    result.reset_call=0xed0d0U; result.initial_format_call=0xeaf20U;
    result.initial_format_x=18U; result.initial_format_y=6U;
    result.prompt_string_address=event_mode_flag ? 0xed1e0U : 0xed200U;
    result.prompt_renderer=0xf5100U; result.menu_renderer=0xecd80U;
    result.event_mode_flag=event_mode_flag; result.dispatch_counter=dispatch_counter;
    result.dispatch_handler_table=0xecb50U; result.dispatch_save_address=0xe80004U;
    result.dispatch_handler_address = dispatch_counter < 25U ? handlers[dispatch_counter] : 0U;
    result.fallback_call=0xeade8U; result.fallback_status_value=0U;
    result.fallback_save_address=0x578500U; result.status_counter_address=0x578510U;
    if (event_mode_flag != 0U) {
        result.fallback_status_value = fallback_result != 0U ? 2U : 0U;
        result.return_target=0xed300U;
    } else {
        result.return_target=0xed2e0U;
    }
    return result;
}
