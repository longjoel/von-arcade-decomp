/* Runtime record workspace reset recovered from i960 0xed0d0-ed1cc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 result_slot_address[6];
    recovered_u32 result_slot_value[6];
    recovered_u32 primary_slot_address[6];
    recovered_u32 alternate_slot_address[4];
    recovered_u32 parallel_slot_address[13];
    recovered_u32 continuation_address;
    recovered_u32 return_target;
} recovered_runtime_record_workspace_reset_result_ed0d0;

recovered_runtime_record_workspace_reset_result_ed0d0
recovered_runtime_record_workspace_reset_ed0d0(void)
{
    recovered_runtime_record_workspace_reset_result_ed0d0 result = {
        {0x578530U,0x578534U,0x578538U,0x57853cU,0x578540U,0x578544U},
        {0xffffffffU,0xffffffffU,0xffffffffU,0xffffffffU,0xffffffffU,0xffffffffU},
        {0x578548U,0x57854cU,0x578550U,0x578554U,0x578558U,0x57855cU},
        {0x578560U,0x578564U,0x578568U,0x57856cU},
        {0x578570U,0x578574U,0x578578U,0x57857cU,0x578580U,0x578584U,
         0x578588U,0x57858cU,0x578590U,0x578594U,0x578598U,0x57859cU,0x5785a0U},
        0xed1d0U, 0xed1ccU
    };
    return result;
}
