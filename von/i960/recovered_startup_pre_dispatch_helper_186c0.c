/* Startup device-command wrapper recovered from i960 0x186c0-0x186e4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_pre_dispatch_plan {
    u32 command_byte;
    u32 command_cleared;
    u32 buffer_address;
    u32 clear_byte_count;
    u32 clear_helper;
};

void recovered_startup_pre_dispatch_helper_186c0(
    struct recovered_startup_pre_dispatch_plan *plan)
{
    plan->command_byte = 3U;
    plan->command_cleared = 1U;
    plan->buffer_address = 0x005770c0U;
    plan->clear_byte_count = 16U;
    plan->clear_helper = 0x000c5d48U;
}
