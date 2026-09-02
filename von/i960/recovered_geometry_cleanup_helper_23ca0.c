/* Indirect geometry cleanup helper recovered from i960 0x23ca0-0x23cd8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_cleanup_plan {
    u32 return_stub;
    u32 cleared_object_byte_count;
    u32 cleared_object_byte_offset[3];
    u32 published_constant;
    u32 published_address_count;
    u32 published_address[2];
};

void recovered_geometry_cleanup_plan(
    struct recovered_geometry_cleanup_plan *plan)
{
    plan->return_stub = 0x00023cd8U;
    plan->cleared_object_byte_count = 3U;
    plan->cleared_object_byte_offset[0] = 0xa0U;
    plan->cleared_object_byte_offset[1] = 0xa1U;
    plan->cleared_object_byte_offset[2] = 0xa2U;
    plan->published_constant = 0x41200000U;
    plan->published_address_count = 2U;
    plan->published_address[0] = 0x00504d54U;
    plan->published_address[1] = 0x00504d58U;
}
