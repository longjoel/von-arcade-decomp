/* Alternate record pipeline dispatcher recovered from i960 0xec8f0-ec91c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 preparation_call[4];
    recovered_u32 zero_argument;
    recovered_u32 builder_call;
    recovered_u32 status_counter_before;
    recovered_u32 status_counter_after;
    recovered_u32 status_counter_address;
    recovered_u32 return_target;
} recovered_runtime_alt_record_pipeline_dispatch_result_ec8f0;

recovered_runtime_alt_record_pipeline_dispatch_result_ec8f0
recovered_runtime_alt_record_pipeline_dispatch_ec8f0(
    recovered_u32 status_counter_before)
{
    recovered_runtime_alt_record_pipeline_dispatch_result_ec8f0 result;
    result.preparation_call[0] = 0x00029a80U;
    result.preparation_call[1] = 0x0001c220U;
    result.preparation_call[2] = 0x0001bda0U;
    result.preparation_call[3] = 0x00028840U;
    result.zero_argument = 0U;
    result.builder_call = 0x000ec820U;
    result.status_counter_before = status_counter_before;
    result.status_counter_after = status_counter_before + 1U;
    result.status_counter_address = 0x00578510U;
    result.return_target = 0x000ec91cU;
    return result;
}
