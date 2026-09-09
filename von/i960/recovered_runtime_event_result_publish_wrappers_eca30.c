/* Event-result checksum publishers recovered from i960 0xeca30-ecb48. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 entry_address, source_base, input_byte_count;
    recovered_u32 checksum_variant, output_address;
    recovered_u32 checksum_continuation, status_counter_before;
    recovered_u32 status_counter_after, status_counter_address;
    recovered_u32 return_target;
} recovered_runtime_event_result_publish_result;

int recovered_runtime_event_result_publish_wrapper(
    recovered_u32 entry_address, recovered_u32 status_counter_before,
    recovered_runtime_event_result_publish_result *result)
{
    recovered_runtime_event_result_publish_result local;
    local.entry_address = entry_address;
    local.status_counter_before = status_counter_before;
    local.status_counter_after = status_counter_before + 1U;
    local.status_counter_address = 0x00578510U;
    local.return_target = entry_address + 0x28U;
    local.source_base = 0U; local.input_byte_count = 0U;
    local.checksum_variant = 0U; local.output_address = 0U;
    local.checksum_continuation = 0U;
    switch (entry_address) {
    case 0x000eca30U: local.source_base=0x02000000U; local.input_byte_count=0x800000U; local.checksum_variant=4U; local.output_address=0x578538U; local.checksum_continuation=0xec9c0U; break;
    case 0x000eca60U: local.source_base=0x02000000U; local.input_byte_count=0x800000U; local.checksum_variant=3U; local.output_address=0x57853cU; local.checksum_continuation=0xeca28U; break;
    case 0x000eca90U: local.source_base=0x02800000U; local.input_byte_count=0x800000U; local.checksum_variant=4U; local.output_address=0x578530U; local.checksum_continuation=0xec9c0U; break;
    case 0x000ecac0U: local.source_base=0x02800000U; local.input_byte_count=0x800000U; local.checksum_variant=3U; local.output_address=0x578534U; local.checksum_continuation=0xeca28U; break;
    case 0x000ecaf0U: local.source_base=0x01000000U; local.input_byte_count=0x01000000U; local.checksum_variant=4U; local.output_address=0xec9c0U; local.output_address=0x578540U; local.checksum_continuation=0xec9c0U; break;
    case 0x000ecb20U: local.source_base=0x01000000U; local.input_byte_count=0x01000000U; local.checksum_variant=3U; local.output_address=0x578544U; local.checksum_continuation=0xeca28U; break;
    default: if (result != (recovered_runtime_event_result_publish_result *)0) *result=local; return 0;
    }
    if (result != (recovered_runtime_event_result_publish_result *)0) *result=local;
    return 1;
}
