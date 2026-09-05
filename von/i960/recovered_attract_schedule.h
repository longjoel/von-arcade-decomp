#ifndef VON_RECOVERED_ATTRACT_SCHEDULE_H
#define VON_RECOVERED_ATTRACT_SCHEDULE_H

typedef unsigned int recovered_schedule_u32;

enum recovered_attract_phase {
    RECOVERED_ATTRACT_BOOT = 0U,
    RECOVERED_ATTRACT_SEGA_LOGO = 1U,
    RECOVERED_ATTRACT_MACHINE_SELECT = 2U,
    RECOVERED_ATTRACT_TAKEOFF = 3U,
    RECOVERED_ATTRACT_LEVEL_INTRO = 4U,
    RECOVERED_ATTRACT_MATCH_ENTRY = 5U,
};

enum recovered_attract_event {
    RECOVERED_ATTRACT_EVENT_NONE = 0U,
    RECOVERED_ATTRACT_EVENT_SEGA_LOGO = 1U,
    RECOVERED_ATTRACT_EVENT_MACHINE_SELECT = 2U,
    RECOVERED_ATTRACT_EVENT_TAKEOFF = 3U,
    RECOVERED_ATTRACT_EVENT_LEVEL_INTRO = 4U,
    RECOVERED_ATTRACT_EVENT_MATCH_ENTRY = 5U,
};

void recovered_attract_step(recovered_schedule_u32 tick,
                            recovered_schedule_u32 phase,
                            recovered_schedule_u32 *next_phase,
                            recovered_schedule_u32 *event);

recovered_schedule_u32 recovered_attract_next_phase(
    recovered_schedule_u32 tick,
    recovered_schedule_u32 phase);

#endif
