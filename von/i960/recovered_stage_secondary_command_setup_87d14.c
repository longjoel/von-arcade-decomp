/* Secondary command/setup bridge recovered from i960 0x87d14-0x87d38. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_command_setup_87d14 {
    u32 first_service_target;
    u32 first_service_argument;
    u32 formatter_target;
    u32 formatter_argument_0;
    u32 formatter_argument_1;
    u32 controller_value;
    u32 controller_mask;
    u32 controller_service_target;
};

struct recovered_stage_secondary_command_setup_87d14
recovered_stage_secondary_command_setup_87d14(u32 controller_value)
{
    struct recovered_stage_secondary_command_setup_87d14 out;

    out.first_service_target = 0x00023d60U;
    out.first_service_argument = 1U;
    out.formatter_target = 0x0001cac8U;
    out.formatter_argument_0 = 21U;
    out.formatter_argument_1 = 14U;
    out.controller_value = controller_value;
    out.controller_mask = controller_value & 4U;
    out.controller_service_target = 0x0001fe60U;
    return out;
}
