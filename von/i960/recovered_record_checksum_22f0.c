/* Backup-SRAM record checksum writer recovered from i960 0x22f0-0x2320. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_record_checksum_plan {
    u32 checksum_helper;
    u32 record_base;
    u32 record_stride;
    u32 data_offset;
    u32 checksum_offset;
    u32 byte_count;
    u32 byte_stride;
    u32 checksum_mask;
    u32 data_address;
    u32 checksum_address;
};

void recovered_record_checksum_plan(u32 index,
                                    struct recovered_record_checksum_plan *plan)
{
    u32 offset = index * 524U;

    plan->checksum_helper = 0x00003120U;
    plan->record_base = 0x01d00000U;
    plan->record_stride = 524U;
    plan->data_offset = 0x16U;
    plan->checksum_offset = 0x14U;
    plan->byte_count = 34U;
    plan->byte_stride = 1U;
    /* The stos/ldos pair moves halfwords: only the low 16 bits of the
     * 0x3120 result are stored, and the 0x2594/0x2604 verifiers mask both
     * sides with 0xffff before comparing. */
    plan->checksum_mask = 0xffffU;
    plan->data_address = 0x01d00016U + offset;
    plan->checksum_address = 0x01d00014U + offset;
}
