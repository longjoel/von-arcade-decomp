/* Runtime ROM-bank orchestrator recovered from i960 0xeb830-eb898. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 selector_entry;
    recovered_u32 loader_count;
    recovered_u32 loader_entry[8];
    recovered_u32 mismatch_slot_address[2];
    recovered_u32 normalized_mismatch_value;
    recovered_u32 mismatch_558_before;
    recovered_u32 mismatch_55c_before;
    recovered_u32 mismatch_558_after;
    recovered_u32 mismatch_55c_after;
    recovered_u32 status_counter_before;
    recovered_u32 status_counter_after;
    recovered_u32 status_counter_address;
    recovered_u32 return_target;
} recovered_runtime_rom_bank_load_all_result_eb830;

recovered_runtime_rom_bank_load_all_result_eb830
recovered_runtime_rom_bank_load_all_eb830(
    recovered_u32 mismatch_558_before, recovered_u32 mismatch_55c_before,
    recovered_u32 status_counter_before)
{
    recovered_runtime_rom_bank_load_all_result_eb830 result;
    static const recovered_u32 loader_entry[8] = {
        0x000eb5b0U, 0x000eb600U, 0x000eb650U, 0x000eb6a0U,
        0x000eb6f0U, 0x000eb740U, 0x000eb790U, 0x000eb7e0U
    };
    recovered_u32 i;

    result.selector_entry = 0x000eb3b8U;
    result.loader_count = 8U;
    for (i = 0U; i < 8U; ++i)
        result.loader_entry[i] = loader_entry[i];
    result.mismatch_slot_address[0] = 0x00578558U;
    result.mismatch_slot_address[1] = 0x0057855cU;
    result.normalized_mismatch_value = 1U;
    result.mismatch_558_before = mismatch_558_before;
    result.mismatch_55c_before = mismatch_55c_before;
    result.mismatch_558_after = mismatch_558_before == 0U ? 1U : mismatch_558_before;
    result.mismatch_55c_after = mismatch_55c_before == 0U ? 1U : mismatch_55c_before;
    result.status_counter_before = status_counter_before;
    result.status_counter_after = status_counter_before + 1U;
    result.status_counter_address = 0x00578510U;
    result.return_target = 0x000eb898U;
    return result;
}
