/* Pure boot/title/attract scheduler shared by the i960 image and Linux tests. */

#include "recovered_attract_schedule.h"

recovered_schedule_u32 recovered_attract_next_phase(
    recovered_schedule_u32 tick,
    recovered_schedule_u32 phase)
{
    switch (phase) {
    case RECOVERED_ATTRACT_BOOT:
        return tick >= 4300000U ? RECOVERED_ATTRACT_SEGA_LOGO : phase;
    case RECOVERED_ATTRACT_SEGA_LOGO:
        return tick >= 4900000U ? RECOVERED_ATTRACT_MACHINE_SELECT : phase;
    case RECOVERED_ATTRACT_MACHINE_SELECT:
        return tick >= 5200000U ? RECOVERED_ATTRACT_TAKEOFF : phase;
    case RECOVERED_ATTRACT_TAKEOFF:
        return tick >= 5800000U ? RECOVERED_ATTRACT_LEVEL_INTRO : phase;
    case RECOVERED_ATTRACT_LEVEL_INTRO:
        return tick >= 6800000U ? RECOVERED_ATTRACT_MATCH_ENTRY : phase;
    case RECOVERED_ATTRACT_MATCH_ENTRY:
    default:
        return phase;
    }
}

void recovered_attract_step(recovered_schedule_u32 tick,
                            recovered_schedule_u32 phase,
                            recovered_schedule_u32 *next_phase,
                            recovered_schedule_u32 *event)
{
    recovered_schedule_u32 next = recovered_attract_next_phase(tick, phase);
    *next_phase = next;
    *event = RECOVERED_ATTRACT_EVENT_NONE;
    if (next != phase)
        *event = next;
}
