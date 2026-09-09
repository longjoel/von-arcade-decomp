/* Bounded state writes from the geometry-runtime initializer at 0x95910. */
#include "recovered_common.h"

struct recovered_geometry_runtime_state_init_95910_plan {
    recovered_u32 seed_table_address, seed_word, seed_record_count;
    recovered_u32 clear_table_address, clear_record_count;
    recovered_u32 global_5624ac_address, global_5624ac_value;
    recovered_u32 global_5624b8_address, global_5624b8_value;
    recovered_u32 global_5624c4_address, global_5624c4_value;
};

void recovered_geometry_runtime_state_init_95910(
    recovered_u32 bal_result, recovered_u32 r9_value,
    recovered_u32 seed_record_count, recovered_u32 (*seed_records)[3],
    recovered_u32 (*clear_records)[3],
    struct recovered_geometry_runtime_state_init_95910_plan *plan)
{
    for (recovered_u32 i = 0; i < seed_record_count; ++i) {
        seed_records[i][0] = bal_result;
        seed_records[i][1] = bal_result;
        seed_records[i][2] = bal_result;
    }
    for (recovered_u32 i = 0; i < 4U; ++i) {
        clear_records[i][0] = 0U;
        clear_records[i][1] = 0U;
        clear_records[i][2] = 0U;
    }

    plan->seed_table_address = 0x562490U;
    plan->seed_word = bal_result;
    plan->seed_record_count = seed_record_count;
    plan->clear_table_address = 0x562500U;
    plan->clear_record_count = 4U;
    plan->global_5624ac_address = 0x5624acU;
    plan->global_5624ac_value = r9_value + 31U;
    plan->global_5624b8_address = 0x5624b8U;
    plan->global_5624b8_value = 0xb4U;
    plan->global_5624c4_address = 0x5624c4U;
    plan->global_5624c4_value = 0xfaU;
}
