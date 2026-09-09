/* Shared event preparation tail recovered from i960 0xea6fc-0xea740. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 derived_value;
    recovered_u32 state_3e8;
    recovered_u32 state_3e8_address;
    recovered_u32 state_base_address;
    recovered_u32 packet[4];
    recovered_u32 packet_count;
    recovered_u32 fifo_address;
    recovered_u32 store_state;
    recovered_u32 next_target;
} recovered_geometry_runtime_event_prepare_result_ea6fc;

recovered_geometry_runtime_event_prepare_result_ea6fc
recovered_geometry_runtime_event_prepare_ea6fc(recovered_u32 derived_value)
{
    recovered_geometry_runtime_event_prepare_result_ea6fc result;

    result.derived_value = derived_value;
    result.state_3e8 = derived_value;
    result.state_3e8_address = 0x005783e8U;
    result.state_base_address = 0x005783e4U;
    result.packet[0] = 20U;
    result.packet[1] = 0x005783e8U;
    result.packet[2] = 21U;
    result.packet[3] = 0U - 0x005783e4U;
    result.packet_count = 4U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.store_state = 1U;
    result.next_target = 0x000ea9a0U;
    return result;
}
