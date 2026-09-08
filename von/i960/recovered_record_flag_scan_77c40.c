/* Structural plan recovered from i960 0x77c40-0x77dd0. */
#include <stdint.h>

struct recovered_record_flag_scan_77c40_plan {
    uint32_t record_base_offset;
    uint32_t record_stride;
    uint32_t record_count;
    uint32_t output_address;
    uint32_t count_threshold;
    uint32_t first_pass_count_bit;
    uint32_t first_pass_output_bits;
    uint32_t second_pass_count_bit;
    uint32_t second_pass_output_bits;
};

/* The register-derived second-pass comparison is intentionally not guessed. */
void recovered_record_flag_scan_77c40_plan(
    struct recovered_record_flag_scan_77c40_plan *plan)
{
    plan->record_base_offset = 0x200U;
    plan->record_stride = 0x20U;
    plan->record_count = 32U;
    plan->output_address = 0x00504e50U;
    plan->count_threshold = 20U;
    plan->first_pass_count_bit = 13U;
    plan->first_pass_output_bits = (1U << 3) | (1U << 6) | (1U << 7);
    plan->second_pass_count_bit = 13U;
    plan->second_pass_output_bits = (1U << 4) | (1U << 2) | (1U << 5);
}
