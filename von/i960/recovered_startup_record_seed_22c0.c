/* Startup record seed recovered from i960 0x22c0-0x22e4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_record_seed_plan {
    u32 copy_helper;
    u32 copy_source;
    u32 copy_destination;
    u32 copy_length;
    u32 type_address;
    u32 type_value;
};

void recovered_startup_record_seed_plan(
    struct recovered_startup_record_seed_plan *plan)
{
    plan->copy_helper = 0x000f5d40U;
    plan->copy_source = 0x000022a0U;
    plan->copy_destination = 0x01d00016U;
    plan->copy_length = 20U;
    plan->type_address = 0x01d00028U;
    plan->type_value = 2U;
}
