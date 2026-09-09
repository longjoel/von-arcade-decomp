/* Diagnostic result formatters recovered from i960 0xecbe0-ecc98. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 entry_address, value_helper, renderer;
    recovered_u32 format_string_address, selected_status_string;
    recovered_u32 status_value, expected_value, has_expected_value;
} recovered_diagnostic_result_format_result;

recovered_diagnostic_result_format_result
recovered_diagnostic_result_format_ecbe0(recovered_u32 status_value)
{
    recovered_diagnostic_result_format_result result;
    result.entry_address=0xecbe0U; result.value_helper=0x1cac8U; result.renderer=0xf5100U;
    result.format_string_address=0xecbb8U; result.status_value=status_value;
    result.expected_value=0U; result.has_expected_value=0U;
    result.selected_status_string = status_value == 1U ? 0xecbc0U : status_value == 0U ? 0xecbc8U : 0xecbd0U;
    return result;
}

recovered_diagnostic_result_format_result
recovered_diagnostic_result_format_compare_ecc40(
    recovered_u32 status_value, recovered_u32 expected_value)
{
    recovered_diagnostic_result_format_result result;
    result.entry_address=0xecc40U; result.value_helper=0x1cac8U; result.renderer=0xf5100U;
    result.format_string_address=0xecbb8U; result.status_value=status_value;
    result.expected_value=expected_value; result.has_expected_value=1U;
    result.selected_status_string = status_value == 0xffffffffU ? 0xecbc8U :
                                    status_value == expected_value ? 0xecbc0U : 0xecc30U;
    return result;
}
