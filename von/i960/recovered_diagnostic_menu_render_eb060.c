/* Diagnostic-menu render plan recovered from i960 0xeb060-eb1b8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 column;
    recovered_u32 row;
    recovered_u32 string_address;
    recovered_u32 wrapper_variant;
} recovered_diagnostic_menu_entry_eb060;

typedef struct {
    recovered_diagnostic_menu_entry_eb060 entry[14];
    recovered_u32 entry_count;
    recovered_u32 selected_value;
    recovered_u32 selected_shifted;
    recovered_u32 marker_clear_address;
    recovered_u32 marker_selected_address;
    recovered_u32 marker_clear_value;
    recovered_u32 marker_selected_value;
    recovered_u32 marker_mode_nonzero;
    recovered_u32 return_target;
} recovered_diagnostic_menu_render_result_eb060;

recovered_diagnostic_menu_render_result_eb060
recovered_diagnostic_menu_render_eb060(recovered_u32 selected_value)
{
    recovered_diagnostic_menu_render_result_eb060 result;
    static const recovered_u32 columns[14] = {
        7U, 13U, 15U, 17U, 19U, 21U, 23U, 25U, 27U, 29U, 31U, 33U, 40U, 41U
    };
    static const recovered_u32 rows[14] = {
        23U, 23U, 23U, 23U, 23U, 23U, 23U, 23U, 23U, 23U, 23U, 23U, 19U, 21U
    };
    static const recovered_u32 strings[14] = {
        0x000eaf40U, 0x000eaf50U, 0x000eaf60U, 0x000eaf70U,
        0x000eaf80U, 0x000eaf90U, 0x000eafa0U, 0x000eafb0U,
        0x000eafd0U, 0x000eaff0U, 0x000eb000U, 0x000eb018U,
        0x000eb020U, 0x000eb040U
    };
    recovered_u32 i;

    for (i = 0U; i < 14U; ++i) {
        result.entry[i].column = columns[i];
        result.entry[i].row = rows[i];
        result.entry[i].string_address = strings[i];
        result.entry[i].wrapper_variant = i == 0U ? 2U : 0U;
    }
    result.entry_count = 14U;
    result.selected_value = selected_value;
    result.selected_shifted = selected_value << 8U;
    result.marker_clear_address = selected_value == 0U
        ? 0x010050aaU : 0x010045aaU + result.selected_shifted;
    result.marker_selected_address = 0x010046aaU + result.selected_shifted;
    result.marker_clear_value = 0U;
    result.marker_selected_value = 30U;
    result.marker_mode_nonzero = selected_value != 0U;
    result.return_target = selected_value == 0U ? 0x000eb1b4U : 0x000eb19cU;
    return result;
}
