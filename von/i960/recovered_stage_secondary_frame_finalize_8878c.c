/* Secondary frame finalizer recovered from i960 0x8878c-0x88878. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_51c950;
    recovered_u32 state_51c94c;
    recovered_u32 state_51c954;
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 snapshot_504b98;
    recovered_u32 snapshot_504b9c;
    recovered_u32 snapshot_504ba0;
    recovered_u32 short_504ba8;
    recovered_u32 short_504baa;
    recovered_u32 fifo_word[7];
    recovered_u32 fifo_count;
    recovered_u32 derived_504d28;
    recovered_u32 derived_5770f4;
    recovered_u32 fifo_address;
    recovered_u32 snapshot_base;
    recovered_u32 short_field_address_504ba8;
    recovered_u32 short_field_address_504baa;
    recovered_u32 derived_504d28_address;
    recovered_u32 derived_5770f4_address;
    recovered_u32 return_target;
} recovered_stage_secondary_frame_finalize_8878c_result;

recovered_stage_secondary_frame_finalize_8878c_result
recovered_stage_secondary_frame_finalize_8878c(
    recovered_u32 state_51c950, recovered_u32 state_51c94c,
    recovered_u32 state_51c954, recovered_u32 state_51c940,
    recovered_u32 state_51c944)
{
    recovered_stage_secondary_frame_finalize_8878c_result result;
    recovered_u32 low_51c940 = state_51c940 & 0xffffU;
    recovered_u32 low_51c944 = state_51c944 & 0xffffU;

    result.state_51c950 = state_51c950;
    result.state_51c94c = state_51c94c;
    result.state_51c954 = state_51c954;
    result.state_51c940 = state_51c940;
    result.state_51c944 = state_51c944;
    result.snapshot_504b98 = state_51c950;
    result.snapshot_504b9c = state_51c94c;
    result.snapshot_504ba0 = state_51c954;
    result.short_504ba8 = low_51c944;
    result.short_504baa = low_51c940;
    result.fifo_word[0] = 20U;
    result.fifo_word[1] = low_51c944;
    result.fifo_word[2] = 21U;
    result.fifo_word[3] = 0U - low_51c940;
    result.fifo_word[4] = 18U;
    result.fifo_word[5] = state_51c950 ^ 0x80000000U;
    result.fifo_word[6] = state_51c94c ^ 0x80000000U;
    result.fifo_count = 7U;
    result.derived_504d28 = (low_51c940 & 0x1fffU) >> 4;
    result.derived_5770f4 = ((state_51c950 ^ 0x80000000U) >> 13) & 7U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.snapshot_base = 0x00504b98U;
    result.short_field_address_504ba8 = 0x00504ba8U;
    result.short_field_address_504baa = 0x00504baaU;
    result.derived_504d28_address = 0x00504d28U;
    result.derived_5770f4_address = 0x005770f4U;
    result.return_target = 0x00088878U;
    return result;
}
