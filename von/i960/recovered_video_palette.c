/*
 * Recovered 0x000e1e08 video lookup-table producer.
 *
 * The firmware selects a step and initial offset from the value at
 * 0x01d00027, then fills the 256-entry 16-bit table consumed by the video
 * tile expanders at 0x005775b0.
 */

typedef unsigned short u16;
typedef unsigned long u32;

#define VIDEO_LOOKUP_ENTRIES 256U

static const u16 VIDEO_STEPS[10] = {
    0x00fa, 0x00f5, 0x00f0, 0x00eb, 0x00e6,
    0x00e6, 0x00eb, 0x00f0, 0x00f5, 0x00fa,
};

static const u16 VIDEO_OFFSETS[10] = {
    5, 10, 15, 20, 25, 40, 32, 24, 16, 8,
};

u16 recovered_video_palette_lookup_initialize(u32 selector,
                                               u16 initial,
                                               u16 *lookup,
                                               u16 *selected_step,
                                               u16 *stored_offset)
{
    u32 index = selector - 1U;
    u32 step = 0xffU;
    u32 offset = 0;
    u32 accumulator = 0;
    u32 entry;

    if (index < 10U) {
        step = VIDEO_STEPS[index];
        offset = VIDEO_OFFSETS[index];
    }

    for (entry = 0; entry < VIDEO_LOOKUP_ENTRIES; ++entry) {
        lookup[entry] = (u16)(initial + offset + accumulator / 255U);
        accumulator += step;
    }

    if (selected_step != 0)
        *selected_step = (u16)step;
    if (stored_offset != 0)
        *stored_offset = (u16)offset;
    return lookup[VIDEO_LOOKUP_ENTRIES - 1U];
}
