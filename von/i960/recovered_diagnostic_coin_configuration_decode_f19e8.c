/* Coin configuration decoder recovered from i960 0xf19e8-f1aa8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 source_status_address, source_status_word, packed_index, table_address;
    recovered_u32 lookup_address[4], lookup_value[4];
    recovered_u32 output_address[4], output_value[4];
    recovered_u32 normalized_status, normalized_status_address;
    recovered_u32 service_state_address, service_state_value, return_target;
} recovered_diagnostic_coin_configuration_decode_result_f19e8;

int
recovered_diagnostic_coin_configuration_decode_f19e8(
    recovered_u32 status_word, const recovered_u32 lookup_value[4],
    recovered_diagnostic_coin_configuration_decode_result_f19e8 *result)
{
    recovered_diagnostic_coin_configuration_decode_result_f19e8 local = {0};
    static const recovered_u32 offsets[4] = {0U,2U,1U,3U};
    static const recovered_u32 outputs[4] = {0x01d00035U,0x01d00030U,0x01d00032U,0x01d00036U};
    local.source_status_address=0x01d0002aU; local.source_status_word=status_word;
    local.packed_index=(status_word & 0xffffU) << 2U; local.table_address=0x000ead30U;
    for (recovered_u32 i=0U; i<4U; ++i) {
        local.lookup_address[i]=local.table_address+local.packed_index+offsets[i];
        local.lookup_value[i]=(lookup_value != (void *)0) ? lookup_value[i] : 0U;
        local.output_address[i]=outputs[i]; local.output_value[i]=local.lookup_value[i];
    }
    local.normalized_status=(local.output_value[3] == 1U) ? 1U : 0U;
    local.normalized_status_address=0x01d00034U; local.service_state_address=0x005785b4U;
    local.service_state_value=1U; local.return_target=0x000f1aa8U;
    if (result != (void *)0) *result=local;
    return 1;
}
