/* First-call asset/table initializer recovered from i960 0x8d170-0x8d298. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 paired_source_a, paired_source_b;
    recovered_u32 paired_destination_a, paired_destination_b;
    recovered_u32 paired_bytes, paired_helper, paired_upload_count;
    recovered_u32 fixed_source_a, fixed_source_b;
    recovered_u32 fixed_destination_a, fixed_destination_b;
    recovered_u32 fixed_bytes, fixed_upload_count;
    recovered_u32 indexed_source_a, indexed_source_b;
    recovered_u32 indexed_destination_a, indexed_destination_b;
    recovered_u32 indexed_bytes, indexed_helper, indexed_upload_count;
    recovered_u32 indexed_stride, indexed_limit;
    recovered_u32 table_a, table_b, table_stride, table_limit;
    recovered_u32 table_sentinel, table_write_offset_a, table_write_offset_b;
} recovered_startup_mode4_arm_result_8d170_asset_table_initializer;

int recovered_startup_mode4_arm_8d170_asset_table_initializer(
    recovered_startup_mode4_arm_result_8d170_asset_table_initializer *result)
{
    recovered_startup_mode4_arm_result_8d170_asset_table_initializer r = {0};
    r.paired_source_a = 0x51d5f0U;
    r.paired_source_b = 0x5289f0U;
    r.paired_destination_a = 0x503ad0U;
    r.paired_destination_b = 0x5040d0U;
    r.paired_bytes = 0x600U;
    r.paired_helper = 0xf5d40U;
    r.paired_upload_count = 30U;
    r.fixed_source_a = 0x560df0U;
    r.fixed_source_b = 0x561370U;
    r.fixed_destination_a = 0x565320U;
    r.fixed_destination_b = 0x5658a0U;
    r.fixed_bytes = 0x580U;
    r.fixed_upload_count = 2U;
    r.indexed_source_a = 0x533df0U;
    r.indexed_source_b = 0x54a5f0U;
    r.indexed_destination_a = 0x503cd0U;
    r.indexed_destination_b = 0x5042d0U;
    r.indexed_bytes = 0x400U;
    r.indexed_helper = 0xf5d40U;
    r.indexed_upload_count = 90U;
    r.indexed_stride = 0x400U;
    r.indexed_limit = 90U;
    r.table_a = 0x5618f0U;
    r.table_b = 0x561e90U;
    r.table_stride = 12U;
    r.table_limit = 90U;
    r.table_sentinel = 0xffffU;
    r.table_write_offset_a = 4U;
    r.table_write_offset_b = 8U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
