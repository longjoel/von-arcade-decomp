#ifndef VON_RECOVERED_ATTRACT_PLATFORM_H
#define VON_RECOVERED_ATTRACT_PLATFORM_H

typedef unsigned int recovered_attract_platform_u32;

struct recovered_attract_platform {
    void *opaque;
    void (*present)(void *opaque, recovered_attract_platform_u32 event,
                    recovered_attract_platform_u32 tick);
};

void recovered_attract_present(const struct recovered_attract_platform *platform,
                               recovered_attract_platform_u32 event,
                               recovered_attract_platform_u32 tick);

#endif
