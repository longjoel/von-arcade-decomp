/* Entry gate recovered from i960 0x78dd0-0x78de8. */

#include <stdint.h>

enum recovered_geometry_entry_route_78dd0 {
    RECOVERED_GEOMETRY_ENTRY_PACKET = 0,
    RECOVERED_GEOMETRY_ENTRY_SERVICE_7CBC0 = 1
};

/* These are the actual branch destinations at 0x78de4 and 0x78de8. */
uint32_t recovered_geometry_entry_target_78dd0(
    enum recovered_geometry_entry_route_78dd0 route)
{
    return route == RECOVERED_GEOMETRY_ENTRY_SERVICE_7CBC0
        ? 0x0007cbc0U
        : 0x00078de4U;
}

uint32_t recovered_geometry_entry_route_78dd0(uint32_t object_state)
{
    return object_state == 2U || object_state == 4U
        ? RECOVERED_GEOMETRY_ENTRY_SERVICE_7CBC0
        : RECOVERED_GEOMETRY_ENTRY_PACKET;
}
