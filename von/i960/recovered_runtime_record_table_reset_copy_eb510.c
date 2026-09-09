/* Runtime record reset/copy helper recovered from i960 0xeb510-eb5a8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packed_byte_count;
    recovered_u32 first_target;
    recovered_u32 caller_target;
    recovered_u32 scan_call_count;
    recovered_u32 scan_target[18];
    recovered_u32 scanner_entry;
    recovered_u32 scanner_resume_entry;
    recovered_u32 selected_source;
    recovered_u32 copy_destination;
    recovered_u32 copy_halfword_count;
    recovered_u32 copy_byte_count;
    recovered_u32 source_publication_address;
    recovered_u32 destination_publication_address;
    recovered_u32 return_target;
} recovered_runtime_record_table_reset_copy_result_eb510;

recovered_runtime_record_table_reset_copy_result_eb510
recovered_runtime_record_table_reset_copy_eb510(
    recovered_u32 caller_target, recovered_u32 selected_source)
{
    recovered_runtime_record_table_reset_copy_result_eb510 result;
    recovered_u32 i;

    result.packed_byte_count = 0x00020000U;
    result.first_target = 0xffffU;
    result.caller_target = caller_target;
    result.scan_call_count = 18U;
    result.scan_target[0] = 0xffffU;
    for (i = 1U; i <= 16U; ++i)
        result.scan_target[i] = 1U << (i - 1U);
    result.scan_target[17] = caller_target;
    result.scanner_entry = 0x000eb450U;
    result.scanner_resume_entry = 0x000eb458U;
    result.selected_source = selected_source;
    result.copy_destination = 0x00501cc0U;
    result.copy_halfword_count = 0x00010000U;
    result.copy_byte_count = 0x00020000U;
    result.source_publication_address = 0x00501cc4U;
    result.destination_publication_address = 0x00501cc0U;
    result.return_target = 0x000eb5a8U;
    return result;
}
