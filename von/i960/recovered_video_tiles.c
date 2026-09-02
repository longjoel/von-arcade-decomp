/*
 * Recovered Model 2 video-tile expanders at 0x000e1f20 and 0x000e2040.
 *
 * The firmware receives three indexed bytes per pixel and expands each byte
 * through the 256-entry 16-bit table at 0x005775b0. The three resulting
 * planes occupy separate 0x200-byte tile slots in video memory. The second
 * entry additionally mirrors each 8x8 plane into the following 0x100-byte
 * half of its slot.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned long u32;

#define TILE_PIXELS 64U
#define TILE_SLOT_WORDS 256U
#define MIRRORED_PLANE_OFFSET 128U

static void expand_tile_planes(u32 tile,
                               const u8 *source,
                               const u16 *lookup,
                               u16 *plane0,
                               u16 *plane1,
                               u16 *plane2,
                               u32 mirror)
{
    u32 index = tile * TILE_SLOT_WORDS;
    u32 pixel;

    for (pixel = 0; pixel < TILE_PIXELS; ++pixel) {
        plane0[index + pixel] = lookup[source[0]];
        plane1[index + pixel] = lookup[source[1]];
        plane2[index + pixel] = lookup[source[2]];
        if (mirror != 0) {
            plane0[index + MIRRORED_PLANE_OFFSET + pixel] = plane0[index + pixel];
            plane1[index + MIRRORED_PLANE_OFFSET + pixel] = plane1[index + pixel];
            plane2[index + MIRRORED_PLANE_OFFSET + pixel] = plane2[index + pixel];
        }
        source += 3;
    }
}

/* 0x000e1f20: one 8x8 plane triplet per tile. */
void recovered_video_expand_tile(u32 tile,
                                 const u8 *source,
                                 const u16 *lookup,
                                 u16 *plane0,
                                 u16 *plane1,
                                 u16 *plane2)
{
    expand_tile_planes(tile, source, lookup, plane0, plane1, plane2, 0);
}

/* 0x000e2040: one 8x8 triplet plus a mirrored half per tile. */
void recovered_video_expand_tile_mirrored(u32 tile,
                                          const u8 *source,
                                          const u16 *lookup,
                                          u16 *plane0,
                                          u16 *plane1,
                                          u16 *plane2)
{
    expand_tile_planes(tile, source, lookup, plane0, plane1, plane2, 1);
}

/* 0x000e2120: table-index wrapper around the mirrored e2040 decoder. */
void recovered_video_expand_tile_indexed(u32 tile,
                                         u32 source_index,
                                         const u8 *const source_table[],
                                         const u16 *lookup,
                                         u16 *plane0,
                                         u16 *plane1,
                                         u16 *plane2)
{
    recovered_video_expand_tile_mirrored(tile, source_table[source_index],
                                          lookup, plane0, plane1, plane2);
}
