/* Presentation adapter shared by the i960 runtime and Linux event recorder. */

#include "recovered_attract_platform.h"

void recovered_attract_present(const struct recovered_attract_platform *platform,
                               recovered_attract_platform_u32 event,
                               recovered_attract_platform_u32 tick)
{
    if (platform != 0 && platform->present != 0)
        platform->present(platform->opaque, event, tick);
}
