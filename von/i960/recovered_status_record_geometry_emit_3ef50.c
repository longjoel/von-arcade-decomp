/* Bounded packet/record contract recovered from i960 0x3ef50. */

#include <stdint.h>

struct recovered_status_record_geometry_emit_plan {
    uint32_t pool_address;
    uint32_t record_stride;
    uint32_t record_count;
    uint32_t status_offset;
    uint32_t table_address;
    uint32_t fifo_address;
    uint32_t packet_selectors[4];
    uint32_t packet_selector_count;
    uint32_t response_offsets[2];
    uint32_t constant_offset;
    uint32_t constant_word;
    uint32_t final_zero_offset;
};

void recovered_status_record_geometry_emit_plan(
    struct recovered_status_record_geometry_emit_plan *plan)
{
    plan->pool_address = 0x0051ad10U;
    plan->record_stride = 0x24U;
    plan->record_count = 23U;
    plan->status_offset = 2U;
    plan->table_address = 0x0003eca0U;
    plan->fifo_address = 0x00884000U;
    plan->packet_selectors[0] = 8U;
    plan->packet_selectors[1] = 13U;
    plan->packet_selectors[2] = 29U;
    plan->packet_selectors[3] = 30U;
    plan->packet_selector_count = 4U;
    plan->response_offsets[0] = 0x0eU;
    plan->response_offsets[1] = 0x16U;
    plan->constant_offset = 0x12U;
    plan->constant_word = 0xbe99999aU;
    plan->final_zero_offset = 0x00U;
}

uint32_t recovered_status_record_geometry_selector(uint32_t value)
{
    return value & 0xffffU;
}
