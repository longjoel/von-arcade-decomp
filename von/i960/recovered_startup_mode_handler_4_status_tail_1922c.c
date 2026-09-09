/* Shared status/dispatch tail of startup mode handler 4, 0x1922c-0x19358. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_address, status_word;
    recovered_u32 maintenance_call, maintenance_call_count;
    recovered_u32 maintenance_phase_low, maintenance_phase_high;
    recovered_u32 copy_call, copy_source, copy_destination, copy_length;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 ready_address, ready_value, hardware_mode_address, hardware_mode_value;
    recovered_u32 bank_window_low, bank_window_high, bank_window_passed;
    recovered_u32 primary_source_address[5], primary_value[5];
    recovered_u32 fallback_source_address[3], fallback_value[3];
    recovered_u32 selected_bank;
    recovered_u32 publication_address[3], publication_value[3], publication_count;
    recovered_u32 table_address, table_index, selected_handler, dispatch_taken;
    recovered_u32 mode_address, mode_before, mode_after;
    recovered_u32 return_target;
} recovered_startup_mode_handler_4_status_tail_result_1922c;

int recovered_startup_mode_handler_4_status_tail_1922c(
    recovered_u32 status_word, recovered_u32 phase, recovered_u32 ready_value,
    recovered_u32 hardware_mode, recovered_u32 mode_value,
    const recovered_u32 table[64],
    const recovered_u32 primary[5], const recovered_u32 fallback[3],
    recovered_startup_mode_handler_4_status_tail_result_1922c *result)
{
    recovered_startup_mode_handler_4_status_tail_result_1922c r = {0};
    static const recovered_u32 primary_addresses[5] = {
        0x502a36U, 0x502a3bU, 0x502a3cU, 0x502a41U, 0x502a40U
    };
    static const recovered_u32 fallback_addresses[3] = {
        0x1d00020U, 0x1d00025U, 0x1d00024U
    };
    r.status_address = 0x5023f2U;
    r.status_word = status_word;
    r.maintenance_call = 0x1e030U;
    r.maintenance_phase_low = 7U;
    r.maintenance_phase_high = 18U;
    r.maintenance_call_count = (status_word != 0U && phase >= 7U && phase <= 18U) ? 1U : 0U;
    r.copy_call = 0xf5d40U;
    r.copy_source = 0x503832U;
    r.copy_destination = 0x1d00016U;
    r.copy_length = 20U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase;
    r.phase_after = phase;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.hardware_mode_address = 0x503a08U;
    r.hardware_mode_value = hardware_mode;
    r.bank_window_low = 7U;
    r.bank_window_high = 10U;
    /* subo 7,phase followed by cmpobl 3 admits exactly 7..10;
     * phases 0..6 underflow and take the branch to 0x1930c. */
    r.bank_window_passed = (phase >= 7U && phase <= 10U &&
                            ready_value != 0U && hardware_mode != 0U) ? 1U : 0U;
    for (recovered_u32 i = 0; i < 5U; ++i) {
        r.primary_source_address[i] = primary_addresses[i];
        r.primary_value[i] = (primary != (void *)0) ? primary[i] : 0U;
    }
    for (recovered_u32 i = 0; i < 3U; ++i) {
        r.fallback_source_address[i] = fallback_addresses[i];
        r.fallback_value[i] = (fallback != (void *)0) ? fallback[i] : 0U;
    }
    r.selected_bank = r.bank_window_passed != 0U ? 1U : 0U;
    r.publication_address[0] = 0x503aa0U;
    r.publication_address[1] = 0x503aa4U;
    r.publication_address[2] = 0x503aa8U;
    r.publication_count = 3U;
    if (r.selected_bank != 0U) {
        r.publication_value[0] = r.primary_value[2];
        r.publication_value[1] = r.primary_value[3] & 0xffU;
        r.publication_value[2] = r.primary_value[4] & 0xffU;
    } else {
        r.publication_value[0] = r.fallback_value[0];
        r.publication_value[1] = r.fallback_value[1] & 0xffU;
        r.publication_value[2] = r.fallback_value[2] & 0xffU;
    }
    r.table_address = 0x18b00U;
    r.table_index = phase & 0x3fU;
    r.selected_handler = (table != (void *)0) ? table[r.table_index] : 0U;
    r.dispatch_taken = r.selected_handler != 0U ? 1U : 0U;
    r.mode_address = 0x5039f4U;
    r.mode_before = mode_value;
    r.mode_after = r.dispatch_taken != 0U ? mode_value : mode_value + 1U;
    if (r.dispatch_taken == 0U)
        r.phase_after = 0U;
    r.return_target = r.dispatch_taken != 0U ? 0x19358U : 0x19350U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
